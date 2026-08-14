#!/usr/bin/env python3
"""liesmich.py — die README schreibt sich selbst fort.

Der Puls-Vertrag verlangt, dass eine Entität dauernd eine BELEGTE Antwort auf
"Wer bin ich? Wann bin ich? In welchem Zustand?" hält. Eine README, die von
Hand gepflegt wird, ist genau das Gegenteil: sie war einmal richtig.

Deshalb steht der handgeschriebene Teil oben und bleibt unangetastet, und
alles zwischen den Marken wird bei jedem Lauf aus dem echten Zustand neu
erzeugt. Kein Modellaufruf, keine Deutung — nur Zählen und Datieren.
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone

WURZEL = os.environ.get("MICROCLAY_WURZEL", "/opt/microclay")
README = os.path.join(WURZEL, "README.md")
ANFANG = "<!-- STAND:ANFANG — erzeugt, nicht von Hand pflegen -->"
ENDE = "<!-- STAND:ENDE -->"

sys.path.insert(0, os.path.join(WURZEL, "clay"))


def _zahl(con, tabelle):
    try:
        return con.execute(f"SELECT count(*) FROM {tabelle}").fetchone()[0]
    except sqlite3.Error:
        return None


def _git(*args):
    try:
        return subprocess.run(["git", "-C", WURZEL, *args], capture_output=True,
                              text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def stand() -> str:
    z = [ANFANG, "", "## Stand", ""]
    jetzt = datetime.now(timezone.utc)
    z.append(f"Erzeugt: **{jetzt.strftime('%Y-%m-%d %H:%M UTC')}** · "
             f"Wirt: `{os.uname().nodename}`")
    z.append("")

    # --- Identität: das Register ist die Wahrheit über die Entitäten ---
    try:
        import identitaet as I
        s = I.register_stand()
        z.append("### Prägestelle")
        z.append("")
        z.append("```")
        z.append(f"Kennungen   {s['kennungen']}")
        z.append(f"Linien      {s['linien']}")
        z.append(f"Ereignisse  {s['ereignisse']}")
        for art, n in sorted(s["je_geburtsart"].items()):
            z.append(f"  {art:<24} {n}")
        z.append("```")
        z.append("")
        con = sqlite3.connect(I.REGISTER)
        neu = con.execute("SELECT clay_id, geburtsart, geburt_zeit FROM register "
                          "ORDER BY geburt_zeit DESC LIMIT 3").fetchall()
        con.close()
        if neu:
            z.append("Zuletzt geprägt:")
            z.append("")
            for k, a, t in neu:
                z.append(f"* `{k}` — {a}, {t[:19]}")
            z.append("")
    except Exception as e:
        z.append(f"⚠️ Register nicht lesbar: {e}")
        z.append("")

    # --- Puls: was der Zyklus tatsächlich getan hat ---
    # Der Puls gehoert der INSTANZ, nicht der Maschine. microclay praegt
    # Identitaeten; wer damit schlaegt, fuehrt sein eigenes Buch. Deshalb
    # wird beides gesucht: der eigene Ort und der dieser Instanz.
    puls_db = os.environ.get("MICROCLAY_PULS", "/var/lib/microclay/puls.db")
    if not os.path.exists(puls_db) and os.path.exists("/var/lib/clay/wiki.db"):
        puls_db = "/var/lib/clay/wiki.db"

    if os.path.exists(puls_db):
        con = sqlite3.connect(puls_db)
        n = _zahl(con, "puls")
        tab = "puls"
        if n is None:
            n = _zahl(con, "pu_takt")
            tab = "pu_takt"
            # ⚠️ pu_takt schreibt bewusst nur, was etwas sagt — der wahre
            # Taktzaehler steht in pu_lage. Die Zeilenzahl waere zu niedrig.
            try:
                r = con.execute("SELECT wert FROM pu_lage WHERE schluessel='takte_gesamt'").fetchone()
                if r:
                    n = int(r[0])
            except sqlite3.Error:
                pass
        if n is not None:
            z.append("### Puls")
            z.append("")
            z.append("```")
            z.append(f"Takte gesamt          {n}")
            for feld, name in (("modellaufrufe", "davon mit Modellaufruf"),
                               ("delta", "verarbeitete Änderungen")):
                try:
                    w = con.execute(f"SELECT sum({feld}) FROM {tab}").fetchone()[0]
                    z.append(f"{name:<22}{w if w is not None else 0}")
                except sqlite3.Error:
                    pass
            try:
                letzt = con.execute(f"SELECT max(zeit) FROM {tab}").fetchone()[0]
                z.append(f"Letzter Takt          {str(letzt)[:19]}")
            except sqlite3.Error:
                pass
            z.append("```")
            z.append("")
        con.close()
    else:
        z.append("### Puls")
        z.append("")
        z.append("Noch kein Takt gelaufen. Die Prägestelle steht, das Herz nicht.")
        z.append("")

    # --- Der Bau selbst ---
    z.append("### Bestand")
    z.append("")
    z.append("```")
    dateien = 0
    zeilen = 0
    for w, _, fs in os.walk(WURZEL):
        if "/.git" in w:
            continue
        for f in fs:
            if f.endswith(".py"):
                dateien += 1
                try:
                    with open(os.path.join(w, f), encoding="utf-8") as fh:
                        zeilen += sum(1 for _ in fh)
                except OSError:
                    pass
    z.append(f"Python-Dateien   {dateien}")
    z.append(f"Zeilen           {zeilen}")
    commits = _git("rev-list", "--count", "HEAD")
    if commits:
        z.append(f"Commits          {commits}")
    kopf = _git("log", "-1", "--format=%h %cs %s")
    if kopf:
        z.append(f"Zuletzt          {kopf[:70]}")
    z.append("```")
    z.append("")
    z.append("⚠️ Dieser Abschnitt wird bei jedem Lauf neu erzeugt. Was hier steht, "
             "ist gezählt — nicht behauptet. Fehlt eine Zahl, fehlt die Quelle, "
             "und das steht dann auch da.")
    z.append("")
    z.append(ENDE)
    return "\n".join(z)


def schreiben(pfad: str = README) -> str:
    with open(pfad, encoding="utf-8") as f:
        alt = f.read()
    neu_block = stand()
    if ANFANG in alt and ENDE in alt:
        vor = alt.split(ANFANG)[0]
        nach = alt.split(ENDE, 1)[1]
        neu = vor + neu_block + nach
    else:
        neu = alt.rstrip() + "\n\n---\n\n" + neu_block + "\n"
    if neu == alt:
        return "unveraendert"
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(neu)
    return "geschrieben"


if __name__ == "__main__":
    b = sys.argv[1] if len(sys.argv) > 1 else "schreiben"
    if b == "zeigen":
        print(stand())
    elif b == "schreiben":
        print(schreiben())
    else:
        print(f"unbekannt: {b}", file=sys.stderr)
        sys.exit(1)
