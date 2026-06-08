# morefire Claude Code Skills

Sammlung von Claude Code Skills für SEO- und Wettbewerbsanalysen.
Output jeweils als PDF-Report im morefire-Design.

Entwickelt von [Martin Weber](https://www.linkedin.com/in/martinweber-marketing/) für [morefire GmbH](https://www.more-fire.com) — Online Marketing Agentur, Köln.

---

## Enthaltene Skills

### 1. SERP Competitive Analysis

Vollautomatisierte SERP-Wettbewerbsanalyse. Analysiert Google- und Bing-SERPs für vorgegebene Keywords, scrapet Wettbewerber-Seiten und erstellt einen strukturierten Report.

**Was er tut:**
1. SERP abrufen (organisch + Paid Ads + PAA + Related Searches)
2. User Story und Persona-Cluster ableiten
3. Jeden Ranking-Eintrag kategorisieren
4. Jede Seite analysieren: USP, Themen, Tonalität, Preiskommunikation, Trust, Micro-Copy
5. Gap-Analyse: Direktvergleich Top-3 und Top-Wettbewerber pro Kategorie vs. eigene Seite
6. Report als HTML-Deck → PDF

**Installation:**
```bash
claude skill install https://github.com/machtiiin/serp-competitive-analysis
```

**Nutzung:**
```
Analysiere die Google-SERPs für "pv anlage kaufen" für enerix (https://enerix.de)
```

---

### 2. SEO Potential Analysis

Auswertung von ScreamingFrog-Crawl-Daten + Google Search Console als executive-ready PDF.
Bricht große Crawls auf relevantes Potenzial und To-dos herunter — auch für C-Level verständlich.

**Was er analysiert:**
- Seiten-Inventar-Funnel: Gecrawlt → Lebendig → Indexierbar → GSC-Sichtbar → Relevant
- Harte Fehler (4xx/5xx) + Redirect-Chains
- Technische Struktur: Canonical-Analyse, Crawltiefe, verwaiste Seiten
- On-Page-Hygiene: fehlende/doppelte Titles und H1s
- Content-Qualität Q*: Verteilung Thin/Mittel/Rich mit GSC-Cross-Reference
- GSC Indexierungsstatus: warum Google Seiten nicht indexiert (Coverage-Export)
- CTR-Optimierungspotenzial: Seiten in Top 10 mit CTR unter Benchmark
- Cluster-Analyse mit Empfehlung: DEINDEX / OPTIMIEREN / STARK / MONITOR
- Optional: Hreflang-Analyse für mehrsprachige/Multi-TLD-Sites

**Benötigte Dateien:**
| Datei | Quelle | Pflicht |
|---|---|---|
| `internal_html.csv` | SF → Internal → HTML → Export | Ja |
| `gsc_pages.csv` | GSC → Leistung → Seiten → Export | Ja |
| `gsc_coverage.csv` | GSC → Index → Abdeckung → Export | Empfohlen |
| `gsc_queries.csv` | GSC → Leistung → Suchanfragen → Export | Optional |
| `sf_hreflang.csv` | SF → Bulk Export → Hreflang → All | Optional |

**Installation:**
```bash
claude skill install https://github.com/machtiiin/serp-competitive-analysis
```

**Nutzung:**
```
Werte den ScreamingFrog-Crawl für morefire.com aus.
SF: ~/Downloads/internal_html.csv
GSC: ~/Downloads/gsc_pages.csv
GSC Coverage: ~/Downloads/gsc_coverage.csv
```

**Manueller Aufruf:**
```bash
python3 seo-potential-analysis/scripts/analyze_seo.py \
  --sf internal_html.csv \
  --gsc gsc_pages.csv \
  --gsc-coverage gsc_coverage.csv \
  --gsc-queries gsc_queries.csv \
  --brand "Mustermarke" \
  --domain "mustermarke.de" \
  --output ./output/mustermarke-seo-audit.html
```

---

## PDF-Export (beide Skills)

```bash
# Design-Assets in den Output-Ordner kopieren (einmalig):
for f in deck-theme.css deck-stage.js tweaks-panel.jsx export-pdf.mjs; do
  cp templates/$f OUTPUT_VERZEICHNIS/
done

# Puppeteer installieren (einmalig):
cd OUTPUT_VERZEICHNIS && npm install puppeteer

# Server starten:
npx serve -l 4000 .

# PDF exportieren:
node export-pdf.mjs DATEINAME.html
```

---

## Repo-Struktur

```
├── SKILL.md                              # SERP Competitive Analysis Skill
├── README.md
├── CONTRIBUTING.md
├── examples/                             # Beispiel-Outputs
├── references/                           # Analyse-Raster, Design-Referenz
├── templates/                            # morefire Design-System (CSS, JS, Export)
└── seo-potential-analysis/               # SEO Potential Analysis Skill
    ├── SKILL.md
    ├── scripts/
    │   └── analyze_seo.py               # Haupt-Analyse-Script (Python, keine Deps)
    └── references/
        └── sf-export-guide.md           # Anleitung SF + GSC Export
```
