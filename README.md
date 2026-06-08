# SERP Competitive Analysis — Claude Code Skill

Vollautomatisierte SERP-Wettbewerbsanalyse für Claude Code. Analysiert Google- und Bing-SERPs für vorgegebene Keywords, scrapet Wettbewerber-Seiten und erstellt einen strukturierten Report als PDF im morefire-Design.

---

## Was der Skill tut

Gegeben eine Marke, eine URL und ein oder mehrere Keywords:

1. SERP abrufen (organisch + Paid Ads + PAA + Related Searches)
2. User Story und Persona-Cluster aus den SERP-Signalen ableiten
3. Jeden Ranking-Eintrag kategorisieren (Direktwettbewerber, Hersteller, Publisher, ...)
4. Jede Seite nach einheitlichem Raster analysieren: USP, Themen, Tonalität, Preiskommunikation, Trust, Micro-Copy, Persona-Abdeckung
5. Gap-Analyse: Direktvergleich Top-3 und Top-Wettbewerber pro Kategorie vs. eigene Seite
6. Report als HTML-Deck rendern und als PDF exportieren

---

## Installation

```bash
# Claude Code Skill installieren
claude skill install https://github.com/machtiiin/serp-competitive-analysis
```

Oder manuell: `SKILL.md` in deinen Claude Code Skills-Ordner kopieren.

**Voraussetzungen:**
- Claude Code mit BrightData MCP-Connector (für SERP-Abruf und Seiten-Scraping)
- Node.js (für PDF-Export via Puppeteer)
- npm-Package `puppeteer` (einmalig: `npm install puppeteer` im Deck-Ordner)

---

## Nutzung

Einfach in Claude Code eingeben:

```
Analysiere die Google-SERPs für "pv anlage kaufen" für die Marke enerix (https://enerix.de)
```

Der Skill triggert automatisch und führt durch das Briefing.

---

## PDF-Export

Nach der Analyse wird ein HTML-Deck erstellt. Export als PDF:

```bash
# 1. Server starten (im Deck-Ordner)
npx serve -l 4000 .

# 2. PDF exportieren (in separatem Terminal)
node templates/export-pdf.mjs mein-deck/mein-deck.html
# → Output: mein-deck/mein-deck.pdf (1920×1080, Landscape)
```

---

## Repo-Struktur

```
serp-competitive-analysis/
├── SKILL.md                         # Skill-Instruktionen für Claude Code
├── README.md                        # Dieses Dokument
├── CONTRIBUTING.md                  # Wie man den Skill weiterentwickelt
├── references/
│   └── analysis-raster.md           # Analyse-Raster (Referenz)
├── templates/
│   ├── _template.html               # Ausgangspunkt für jedes neue Deck
│   ├── deck-theme.css               # morefire Design-System
│   ├── deck-stage.js                # Web Component <deck-stage>
│   ├── tweaks-panel.jsx             # Live-Farb/Typo-Panel im Browser
│   ├── export-pdf.mjs               # PDF-Export via Puppeteer
│   └── ONBOARDING.md               # Design-System Kurzreferenz
└── examples/
    ├── enerix-photovoltaikanlage.html  # Beispiel-Output (HTML-Deck)
    └── enerix-photovoltaikanlage.pdf  # Beispiel-Output (PDF)
```

---

## Weiterentwicklung

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Hinweise zur Erweiterung des Skills und des Design-Systems.

---

Entwickelt von [Martin Weber](https://www.linkedin.com/in/martinweber-marketing/) für [morefire GmbH](https://www.more-fire.com) — Online Marketing Agentur, Köln.
