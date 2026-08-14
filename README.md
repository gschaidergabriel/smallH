# microclay — kybernetische Mikroentität

Eine minimale, wiederverwendbare Maschine für dauerhafte Kognition.

Gebaut nach der **Frank-Architektur** und dem
`FRANK_DATABASE_PULSE_CONTRACT` (owner-fixed, 2026-08-09): ein endogener
Zustands- und Kognitionszyklus, der **kein** Modellaufruf-Loop ist.

    Ein Puls kann ohne einen einzigen Modellaufruf ablaufen.

## Was es ist

Eine Sammlung **reaktiver Politiken** plus **genau einem lernenden Netz**,
zusammengehalten von einem Zyklus. Nichts darüber hinaus.

Es ist eine **Maschine, keine Anwendung**. ClayVerse ist ihr erster Benutzer,
nicht ihr Zweck. Wer eine Mikroentität mit Zeitsinn, Gedächtnis, Abruf und
Lernen braucht, benutzt sie — für was auch immer.

## Warum es ein eigenes Projekt ist

Die erste Fassung des Puls-Systems scheiterte an einer Frage, die nie
beantwortet war: **wer soll diese immerwährende Kognition eigentlich haben?**

Ohne Träger ist ein Zyklus ein Timer. Deshalb steht die Identität hier an
erster Stelle und nicht am Ende: jede Instanz bekommt eine unveränderliche
**ClayID** aus einer anhängenden Prägestelle, mit Geburtsbeleg und Abstammung.
Erst danach darf sie pulsen.

## Die Gesetze, die nicht verhandelbar sind

    ENTITY          != LLM
    DATABASE_PULSE  != LLM_INFERENCE_LOOP
    ENTITY_NAME     == CLAY_ID
    FRANK           != INDIVIDUAL_NAME

Jede Kopie ist eine **neue** Entität mit eigener ClayID und eigener
Kontinuität. Eine kopierte Instanz darf niemals unter der ClayID ihres
Elters pulsen.

Der abgeleitete Graph wird **nie** zur Wahrheitsinstanz, nur weil etwas stark
aktiviert ist.

## Die Organe — und was davon ein Netz ist

    Zeitsinn      Buchführung          kein Netz
    Gedächtnis    Speicher + Kuration  kein Netz
    Thalamus      epistemisches Tor    kein Netz, eine Regel
    Datenbank     Graph mit gelernten Kanten    ⭐ das eine Netz, lernt online
    Hirn          der Zyklus           kein Netz, ein Ablauf
    Arme/Beine    Reflex               offen, unbelegt

Genau **ein** Organ ist ein Netz. Das ist kein Sparzwang, sondern ein Befund:
was sich als Regel messen lässt, gehört nicht in Gewichte. Ein gelernter
Zeitsinn ist schlechter als eine Uhr.

## Der Zyklus

    1  Zeit fortschreiben, Sprünge erkennen
    2  Identität und Abstammung prüfen
    3  Umgebung fortschreiben
    4  Aktivierung ausbreiten
    5  Hypothesen und Codependencys erzeugen, nur mit Beleg
    6  Auswahl und Weiterleitung
    7  Ungelöste Alternativen offen halten
    8  Regulation
    9  Gedächtnis verdichten, verfallen lassen
   10  OPTIONAL: Modell, Werkzeug, Peer
   11  Ergebnisse aufnehmen
   12  Epoche fortschreiben, Schnappschuss, Eichung

Phase 10 bleibt leer, solange kein Modell nötig ist. Das ist der Normalfall.

## Was gegen Entartung eingebaut ist

Dieses Projekt hat Degeneration zweimal **gemessen**: die Vielfalt in einem
Schwarm halbierte sich je Runde, und ein Thalamus endete mit 6 von 10 Kanälen
im Fixpunkt. Ein Organismus, der entartet, ist schlechter als eine
Nachschlagetabelle.

    Vielfaltsboden   Entropie der Ausgaben je Schnappschuss — fällt sie, ist das
                     das Signal, noch vor dem Qualitätsverlust
    Verfall          gelernte Gewichte klingen ab
    Gegenseite       nie Erkundungsplatz, nie zuerst verworfen
    Eichnormale      feste Prüfsteine, für das Lernende nicht schreibbar
    Heilung          Rücknahme auf den jüngsten Stand, der die Normale bestand

Das Lernende lernt aus dem **Gebrauch**, niemals aus der eigenen Ausgabe.
Das ist der Unterschied zwischen Lernen und Drift.

## Epistemische Grenze

„lebt", „denkt", „Seele" sind hier technische Kurzschrift für eine laufende
Entität mit anhaltenden Zustandsübergängen. Sie begründen **kein** Bewusstsein,
keine Empfindung und keinen moralischen Status. Diese Grenze steht schon im
Puls-Vertrag und wird hier nicht aufgeweicht.

<!-- STAND:ANFANG — erzeugt, nicht von Hand pflegen -->

## Stand

Erzeugt: **2026-08-14 21:04 UTC** · Wirt: `clayverse`

### Prägestelle

```
Kennungen   3
Linien      2
Ereignisse  3
  COPY                     1
  ORIGIN                   2
```

Zuletzt geprägt:

* `clay_01M0115GCHWJF5D751MBK86KJ9` — COPY, 2026-08-14T20:59:38
* `clay_01M0115GCD8FHAPSGNCFSAZG5E` — ORIGIN, 2026-08-14T20:59:38
* `clay_01M011505MVTY0SX8ZEKXSEEN7` — ORIGIN, 2026-08-14T20:59:22

### Puls

Noch kein Takt gelaufen. Die Prägestelle steht, das Herz nicht.

### Bestand

```
Python-Dateien   2
Zeilen           394
Commits          1
Zuletzt          8a84289 2026-08-14 microclay: kybernetische Mikroentitaet — Identitaet
```

⚠️ Dieser Abschnitt wird bei jedem Lauf neu erzeugt. Was hier steht, ist gezählt — nicht behauptet. Fehlt eine Zahl, fehlt die Quelle, und das steht dann auch da.

<!-- STAND:ENDE -->
