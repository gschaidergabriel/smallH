#!/usr/bin/env python3
"""liesmich.py — update the README's local status section.

The manually written documentation remains unchanged. This script replaces
only the marked status block with measurements from local databases and Git.
The report is not a measure of project-wide functionality or performance.
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
ANFANG = "<!-- STATUS:START -->"
ENDE = "<!-- STATUS:END -->"

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
    z = [ANFANG, "", "## Local status (generated)", ""]
    jetzt = datetime.now(timezone.utc)
    z.append(f"Generated: **{jetzt.strftime('%Y-%m-%d %H:%M UTC')}** · "
             f"Host: `{os.uname().nodename}`")
    z.append("")

    # --- Identität: das Register ist die Wahrheit über die Entitäten ---
    try:
        import identitaet as I
        s = I.register_stand()
        z.append("### Identity registry")
        z.append("")
        z.append("```")
        z.append(f"Identities  {s['kennungen']}")
        z.append(f"Lineages    {s['linien']}")
        z.append(f"Events      {s['ereignisse']}")
        for art, n in sorted(s["je_geburtsart"].items()):
            z.append(f"  {art:<24} {n}")
        z.append("```")
        z.append("")
        con = sqlite3.connect(I.REGISTER)
        neu = con.execute("SELECT clay_id, geburtsart, geburt_zeit FROM register "
                          "ORDER BY geburt_zeit DESC LIMIT 3").fetchall()
        con.close()
        if neu:
            z.append("Most recently registered:")
            z.append("")
            for k, a, t in neu:
                z.append(f"* `{k}` — {a}, {t[:19]}")
            z.append("")
    except Exception as e:
        z.append(f"Registry unavailable: {e}")
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
            z.append("### Pulse records")
            z.append("")
            z.append("```")
            z.append(f"Total ticks           {n}")
            for feld, name in (("modellaufrufe", "Model calls"),
                               ("delta", "Changes processed")):
                try:
                    w = con.execute(f"SELECT sum({feld}) FROM {tab}").fetchone()[0]
                    z.append(f"{name:<22}{w if w is not None else 0}")
                except sqlite3.Error:
                    pass
            try:
                letzt = con.execute(f"SELECT max(zeit) FROM {tab}").fetchone()[0]
                z.append(f"Last tick             {str(letzt)[:19]}")
            except sqlite3.Error:
                pass
            z.append("```")
            z.append("")
        con.close()
    else:
        z.append("### Pulse records")
        z.append("")
        z.append("No accessible pulse database. This repository does not include a pulse engine.")
        z.append("")

    # --- Der Bau selbst ---
    z.append("### Repository checkout")
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
    z.append(f"Python files   {dateien}")
    z.append(f"Lines          {zeilen}")
    commits = _git("rev-list", "--count", "HEAD")
    if commits:
        z.append(f"Commits        {commits}")
    kopf = _git("log", "-1", "--format=%h %cs %s")
    if kopf:
        z.append(f"Latest commit  {kopf[:70]}")
    z.append("```")
    z.append("")
    z.append("These figures come from the current host and configured databases. "
             "Unavailable values are omitted; the report does not verify runtime features.")
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
        return "unchanged"
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(neu)
    return "written"


if __name__ == "__main__":
    b = sys.argv[1] if len(sys.argv) > 1 else "schreiben"
    if b == "zeigen":
        print(stand())
    elif b == "schreiben":
        print(schreiben())
    else:
        print(f"unknown command: {b}", file=sys.stderr)
        sys.exit(1)
