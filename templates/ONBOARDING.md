# morefire Slides – Master Template

Das ist der **zentrale Template-Ordner** für alle morefire Slide-Decks. Hier liegen die geteilten Design-Assets (CSS, JS, HTML-Template, PDF-Export). Alle neuen Präsentationen sollen sich von hier bedienen.

**Pfad:** `/Users/r.dege/Documents/Coding/Templates/Design/`

Alle Decks laufen im Browser (1920×1080), werden per `npx serve` gehosted und können als PDF exportiert werden.

## Struktur

```
Coding/
├── Templates/Design/         # ← DU BIST HIER (Master)
│   ├── _template.html        # Ausgangspunkt für jedes neue Deck
│   ├── _design-reference.md  # Design-Regeln, Slide-Typen, Beispiele
│   ├── deck-theme.css        # Globales Styling + CSS-Variablen
│   ├── deck-stage.js         # Web Component <deck-stage>
│   ├── tweaks-panel.jsx      # Live-Farb/Typo-Panel (rechts im Browser)
│   ├── export-pdf.mjs        # PDF-Export via Puppeteer
│   └── ONBOARDING.md         # Dieses Dokument
└── Slides/
    ├── trstd/trstd.html       # Beispiel-Deck
    └── toggo.de/toggo.de.html # Beispiel-Deck
```

## Neues Deck anlegen

Zwei Varianten je nach Setup:

### Variante A — Deck-Ordner direkt unter `Templates/Design/`

```bash
cd /Users/r.dege/Documents/Coding/Templates/Design
mkdir meinprojekt && cp _template.html meinprojekt/meinprojekt.html
```

Im kopierten HTML die `./`-Pfade auf `../` ändern:
- `href="../deck-theme.css"`
- `src="../deck-stage.js"`
- `src="../tweaks-panel.jsx"`

### Variante B — Deck-Ordner an beliebiger Stelle (empfohlen für Kundenprojekte)

Asset-Dateien aus `Templates/Design/` ins Projektverzeichnis kopieren oder symlinken — danach wie in Variante A.

```bash
# Beispiel: neues Kundenprojekt unter Coding/Slides/kunde/
cp /Users/r.dege/Documents/Coding/Templates/Design/{_template.html,deck-theme.css,deck-stage.js,tweaks-panel.jsx,export-pdf.mjs} /Users/r.dege/Documents/Coding/Slides/kunde/
```

### In allen Fällen

3. `<title>`, `TWEAK_DEFAULTS` und Footer-Texte (`Client | Deck title`) anpassen.
4. Placeholder-Slides durch echte Inhalte ersetzen.

## Server starten (Preview)

```bash
# Vom Ordner aus, der die Asset-Dateien enthält:
npx serve -l 4000 .
# Deck öffnen: http://localhost:4000/meinprojekt/meinprojekt.html
```

## PDF-Export

```bash
# Einmalig Puppeteer installieren (im Projektordner):
npm install puppeteer

# Export vom Root aus, in dem die Assets liegen (Server muss laufen):
node export-pdf.mjs meinprojekt/meinprojekt.html
# → Ausgabe: meinprojekt/meinprojekt.pdf (1920×1080, 2×)
```

## Slide-Typen

| Typ | Klasse(n) | Beschreibung |
|-----|-----------|--------------|
| Cover | `s-cover frame-flush` | Rotes Deckblatt |
| Section Divider | `s-section frame-flush` | Schwarze Kapitelseite |
| Content 2-col | `frame` + `cols-2` | Text links, Karte rechts |
| 4-Card Grid | `frame` + `cols-4` | Vier Karten nebeneinander |
| Ghost Cards | inline Grid | Karten mit großer Hintergrundnummer |
| 3-Card Grid | `frame` + `cols-3` | Drei Karten |
| Checklist | `find-row` | Zeilen mit Icon + Pill (gap/warn/ok) |
| Tabelle | — | Dark-Header, Stripe-Rows, Highlight-Row |
| Closing | `s-grey frame frame-centered` | Abschluss-Slide |

## CSS-Variablen (Farben)

| Variable | Bedeutung |
|----------|-----------|
| `var(--c-red)` | Accent (Standard: `#DB3543`) |
| `var(--c-orange)` | Secondary (`#f08262`) |
| `var(--c-black)` | Dunkel (`#1d1d1b`) |
| `var(--c-grey)` | Hellgrau (Karten-Hintergrund) |
| `var(--c-green)` | Positiv |
| `var(--c-ink-60)` / `--c-ink-40` / `--c-ink-15` | Graustufen für Text und Border |

Farben und Schriftgrößen können live über das Tweaks-Panel im Browser angepasst werden.

## Copy-Regeln

- Keine Em-Dashes (`—`) im Slide-Text — Sätze stattdessen umformulieren.

## Aufgaben für Claude

Wenn du Claude bittest, ein neues Deck zu erstellen:
- Sag ihm, welcher Kunde und welches Thema
- Claude legt den Ordner an, kopiert das Template, passt Pfade und TWEAK_DEFAULTS an und befüllt die Slides mit echtem Inhalt
- Bestehende Decks (z.B. `toggo.de/toggo.de.html`) zeigen, wie fertige Slides aussehen
