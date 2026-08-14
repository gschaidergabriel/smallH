#!/usr/bin/env python3
"""identitaet.py — die Prägestelle für ClayIDs.

Die erste Fassung des Puls-Systems scheiterte an einer unbeantworteten Frage:
wer soll diese Kognition eigentlich haben? Ohne Träger ist ein Zyklus ein
Timer. Deshalb steht dieses Modul vor allem anderen.

Gesetze aus FRANK_DATABASE_PULSE_CONTRACT (owner-fixed, 2026-08-09):
  ENTITY_NAME == CLAY_ID          der Name IST die Kennung
  Kennungen werden NIE wiederverwendet, auch nach Löschung nicht
  jede Kopie ist eine NEUE Entität mit eigener Kennung
  eine kopierte Instanz darf NIEMALS unter der Kennung ihres Elters pulsen

Kein Modellaufruf. Kein Netz. Nur Buchführung — aber die trägt alles andere.
"""
import hashlib
import json
import os
import secrets
import sqlite3
import sys
import time
from datetime import datetime, timezone

REGISTER = os.environ.get("MICROCLAY_REGISTER", "/var/lib/microclay/register.db")

GEBURTSARTEN = ("ORIGIN", "COPY", "FORK", "RESTORE_SAME_LINEAGE",
                "MIGRATION_SAME_LINEAGE", "REBUILD_NEW_ENTITY", "IDENTITY_UNCERTAIN")

# Crockford-Base32 wie ULID: ohne I, L, O, U — nicht verwechselbar beim Abtippen
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


class Kollision(Exception):
    """Die Kennung ist bereits vergeben. Neu prägen, niemals übernehmen."""


class KopiengeburtNoetig(Exception):
    """Ein Körper beansprucht eine fremde Kennung. Fail closed, nicht pulsen."""


def _zeitteil(ms: int) -> str:
    """48 Bit Zeit, sortierbar — die Geburtszeit steckt im Namen."""
    zeichen = []
    for _ in range(10):
        zeichen.append(ALPHABET[ms % 32])
        ms //= 32
    return "".join(reversed(zeichen))


def _zufallsteil() -> str:
    """80 Bit Entropie. Aus den Zufallsbits wird KEINE Bedeutung gelesen."""
    return "".join(ALPHABET[secrets.randbelow(32)] for _ in range(16))


def neue_kennung() -> str:
    return "clay_" + _zeitteil(int(time.time() * 1000)) + _zufallsteil()


def _verbinden(pfad: str = REGISTER) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    con = sqlite3.connect(pfad, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=30000")
    con.execute("""CREATE TABLE IF NOT EXISTS register (
        clay_id TEXT PRIMARY KEY,
        eltern_clay_id TEXT,
        linienwurzel_clay_id TEXT NOT NULL,
        geburtsart TEXT NOT NULL,
        geburt_zeit TEXT NOT NULL,
        geburt_monoton REAL NOT NULL,
        wirt TEXT,
        koerper_pfad TEXT,
        koerper_hash TEXT,
        quell_zustand_hash TEXT,
        beleg TEXT NOT NULL
    )""")
    # Anhängend: was hier steht, wird nie geändert und nie gelöscht.
    con.execute("""CREATE TABLE IF NOT EXISTS ereignis (
        nr INTEGER PRIMARY KEY AUTOINCREMENT,
        zeit TEXT NOT NULL, art TEXT NOT NULL,
        clay_id TEXT NOT NULL, inhalt TEXT NOT NULL
    )""")
    con.commit()
    return con


def _datei_hash(pfad: str) -> str | None:
    try:
        h = hashlib.sha256()
        with open(pfad, "rb") as f:
            for block in iter(lambda: f.read(1 << 16), b""):
                h.update(block)
        return h.hexdigest()
    except OSError:
        return None


def praegen(geburtsart: str = "ORIGIN", eltern: str | None = None,
            koerper_pfad: str | None = None, quell_zustand_hash: str | None = None,
            wirt: str | None = None, pfad: str = REGISTER) -> str:
    """Prägt genau eine neue Kennung und schreibt ihren Geburtsbeleg.

    Atomar: die Eindeutigkeit hält der Primärschlüssel, nicht eine Prüfung
    davor. Verliert ein gleichzeitiger Schreiber, prägt er neu — es gibt
    keinen zentralen Zähler, der Autorität hätte.
    """
    if geburtsart not in GEBURTSARTEN:
        raise ValueError(f"unbekannte Geburtsart: {geburtsart}")
    if geburtsart in ("COPY", "FORK") and not eltern:
        raise ValueError(f"{geburtsart} ohne Eltern-Kennung ist keine Abstammung")

    con = _verbinden(pfad)
    try:
        wurzel = None
        if eltern:
            z = con.execute(
                "SELECT linienwurzel_clay_id FROM register WHERE clay_id=?",
                (eltern,)).fetchone()
            if not z:
                raise Kollision(f"Eltern-Kennung {eltern} steht nicht im Register")
            wurzel = z[0]

        for _ in range(8):
            kid = neue_kennung()
            beleg = {
                "geprueft_gegen": "register.clay_id PRIMARY KEY",
                "praegestelle": os.uname().nodename,
                "verfahren": "48bit-Zeit + 80bit-Entropie, Crockford-Base32",
            }
            try:
                con.execute(
                    "INSERT INTO register VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (kid, eltern, wurzel or kid, geburtsart,
                     datetime.now(timezone.utc).isoformat(), time.monotonic(),
                     wirt or os.uname().nodename, koerper_pfad,
                     _datei_hash(koerper_pfad) if koerper_pfad else None,
                     quell_zustand_hash, json.dumps(beleg, ensure_ascii=False)))
                con.execute(
                    "INSERT INTO ereignis (zeit,art,clay_id,inhalt) VALUES (?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), "ENTITY_BIRTH", kid,
                     json.dumps({"geburtsart": geburtsart, "eltern": eltern,
                                 "wurzel": wurzel or kid}, ensure_ascii=False)))
                con.commit()
                return kid
            except sqlite3.IntegrityError:
                continue  # Kollision: neu prägen, niemals übernehmen
        raise Kollision("acht Versuche, acht Kollisionen — das ist ein Befund")
    finally:
        con.close()


def darf_pulsen(kid: str, koerper_pfad: str | None = None,
                pfad: str = REGISTER) -> bool:
    """Vorprüfung vor dem ersten Puls. Fail closed.

    Ein per Dateikopie entstandener Körper trägt die Kennung seines Elters.
    Er darf damit NICHT pulsen — er braucht eine eigene Geburt.
    """
    con = _verbinden(pfad)
    try:
        z = con.execute(
            "SELECT koerper_hash, koerper_pfad FROM register WHERE clay_id=?",
            (kid,)).fetchone()
        if not z:
            raise KopiengeburtNoetig(
                f"{kid} steht nicht im Register — keine Geburt, kein Puls")
        if koerper_pfad and z[0]:
            ist = _datei_hash(koerper_pfad)
            if ist and ist != z[0]:
                raise KopiengeburtNoetig(
                    f"Körper unter {koerper_pfad} passt nicht zum Geburtsbeleg "
                    f"von {kid} — COPY_BIRTH_REQUIRED")
        return True
    finally:
        con.close()


def zeigen(kid: str, pfad: str = REGISTER) -> dict:
    """Wer bin ich, von wem stamme ich, wann wurde ich eigenständig."""
    con = _verbinden(pfad)
    try:
        sp = [s[1] for s in con.execute("PRAGMA table_info(register)")]
        z = con.execute("SELECT * FROM register WHERE clay_id=?", (kid,)).fetchone()
        if not z:
            return {}
        d = dict(zip(sp, z))
        d["ereignisse"] = con.execute(
            "SELECT count(*) FROM ereignis WHERE clay_id=?", (kid,)).fetchone()[0]
        return d
    finally:
        con.close()


def register_stand(pfad: str = REGISTER) -> dict:
    con = _verbinden(pfad)
    try:
        return {
            "kennungen": con.execute("SELECT count(*) FROM register").fetchone()[0],
            "ereignisse": con.execute("SELECT count(*) FROM ereignis").fetchone()[0],
            "je_geburtsart": dict(con.execute(
                "SELECT geburtsart, count(*) FROM register GROUP BY geburtsart")),
            "linien": con.execute(
                "SELECT count(DISTINCT linienwurzel_clay_id) FROM register").fetchone()[0],
        }
    finally:
        con.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    b = sys.argv[1]
    if b == "praegen":
        art = sys.argv[2] if len(sys.argv) > 2 else "ORIGIN"
        el = sys.argv[3] if len(sys.argv) > 3 else None
        print(praegen(art, el))
    elif b == "zeigen":
        print(json.dumps(zeigen(sys.argv[2]), ensure_ascii=False, indent=1))
    elif b == "stand":
        print(json.dumps(register_stand(), ensure_ascii=False, indent=1))
    else:
        print(f"unbekannt: {b}", file=sys.stderr)
        sys.exit(1)
