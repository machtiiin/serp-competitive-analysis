---
name: seo-potential-analysis
description: >
  Erstellt eine executive-ready SEO-Potenzialanalyse aus ScreamingFrog-Crawl-Daten und Google Search Console Daten
  als PDF im morefire-Design. Zeigt Seiten-Inventar-Funnel, harte Fehler (4xx/5xx), On-Page-Hygiene,
  Content-Qualität (Q*-Analyse) und Cluster-basierte Empfehlungen für Deindexierung und Priorisierung.
  Ziel: großen Crawl auf relevantes Potenzial und To-dos herunterbrechen, auch für C-Level verständlich.

  Nutze diesen Skill IMMER wenn jemand sagt: "ScreamingFrog auswerten", "GSC-Daten analysieren",
  "SEO-Potenzialanalyse", "Crawl-Report", "Site-Audit erstellen", "technisches SEO aufbereiten",
  "Content-Qualität analysieren", "welche Seiten soll ich deindexieren" oder wenn ScreamingFrog-
  und/oder Search Console Daten zusammen mit dem Wunsch nach einem Report, einer Auswertung oder
  einem Deck genannt werden.
---

# SEO Potential Analysis — Skill

Automatisierte Auswertung von ScreamingFrog-Crawl-Daten und Google Search Console Daten.
Output: HTML-Deck → PDF-Export im morefire-Design. Ausgerichtet auf C-Level und Entscheider,
nicht auf URL-Listen oder einzelne technische Fehler.

---

## Phase 1 — Briefing

**Alle folgenden Informationen abfragen, bevor du die Analyse startest:**

1. **Marke / Domain** — Name und Domain (z.B. Mustermarke / mustermarke.de)
2. **ScreamingFrog-Export (Pflicht)** — Internal HTML CSV (mit Canonical, Crawl Depth, Inlinks wenn möglich)
3. **GSC Pages-Export (Pflicht)** — Search Console → Leistung → Seiten → CSV
4. **GSC Coverage-Export (empfohlen)** — Search Console → Index → Abdeckung → CSV. Zeigt warum Google Seiten nicht indexiert.
5. **GSC Queries-Export (optional)** — Search Console → Leistung → Suchanfragen → CSV. Für CTR-Analyse.
6. **SF Hreflang-Export (optional, nur bei mehrsprachigen/Multi-TLD-Sites)** — SF → Bulk Export → Hreflang → All
7. **Ausgabe-Verzeichnis** — Wo soll das Deck gespeichert werden? (Standard: ~/Documents/Claude/Slides/)

Falls Pfade nicht klar: auf `references/sf-export-guide.md` verweisen.

---

## Phase 2 — Analyse ausführen

```bash
python3 "SKILL_PATH/scripts/analyze_seo.py" \
  --sf "PFAD/internal_html.csv" \
  --gsc "PFAD/gsc_pages.csv" \
  --brand "MARKE" \
  --domain "domain.de" \
  --output "AUSGABE_PFAD/MARKE-seo-audit.html" \
  [--gsc-coverage "PFAD/gsc_coverage.csv"] \
  [--gsc-queries "PFAD/gsc_queries.csv"] \
  [--sf-hreflang "PFAD/hreflang_all.csv"]
```

`SKILL_PATH` = Verzeichnis dieser SKILL.md-Datei (bei installiertem Skill automatisch bekannt).

---

## Phase 3 — Design-Assets kopieren und PDF exportieren

```bash
# Design-Assets in Output-Ordner kopieren (einmalig):
DESIGN_DIR="~/Documents/Claude/Design"
OUTPUT_DIR="AUSGABE_VERZEICHNIS"
for f in deck-theme.css deck-stage.js tweaks-panel.jsx export-pdf.mjs; do
  cp "$DESIGN_DIR/$f" "$OUTPUT_DIR/"
done

# Puppeteer installieren (falls noch nicht vorhanden):
cd "$OUTPUT_DIR" && npm install puppeteer

# Server starten:
NODE_BIN="/Users/martinweber/.ScreamingFrogSEOSpider/node/5.10/node/bin"
PATH="$NODE_BIN:$PATH" npx serve -l 4000 .

# PDF exportieren:
PATH="$NODE_BIN:$PATH" node export-pdf.mjs MARKE-seo-audit.html
```

---

## Was der Report zeigt (14-15 Slides)

1. Cover mit Marke, Domain, Crawl-Datum
2. Executive Summary — bis zu 5 auto-generierte Kernbefunde
3. Seiten-Inventar — Funnel: Gecrawlt → Lebendig → Indexierbar → GSC-Sichtbar → Relevant
4. Harte Fehler — 4xx/5xx + Weiterleitungen + betroffene Cluster
5. Technische Struktur — Canonical-Analyse, Crawltiefe, verwaiste Seiten (wenn Daten vorhanden)
6. On-Page-Hygiene — fehlende/doppelte Titles und H1s
7. Content-Qualität Q* — Verteilung Thin/Mittel/Rich + GSC-Cross-Reference
8. GSC Indexierungsstatus — Gecrawlt-nicht-indexiert, Gefunden-nicht-indexiert, Soft-404 (wenn Coverage-Export)
9. CTR-Optimierungspotenzial — Seiten in Top 10 mit CTR unter Benchmark
10. Section-Divider
11. Cluster-Analyse — Tabelle mit Empfehlung (inkl. Coverage-Daten wenn vorhanden)
12. Deindex-Kandidaten — Cluster mit 0 Impressionen und/oder Content-Ablehnung durch Google
13. Optimierungsprioritäten — Cluster mit Potenzial (Ranking + CTR)
14. Hreflang (nur wenn --sf-hreflang übergeben)
15. Closing — m.weber@more-fire.com

---

## Daten-Export-Anleitung

Siehe `references/sf-export-guide.md`.

---

## Copy-Regeln

- Keine Em-Dashes (—) im Deck-Text
- Umlaute korrekt: ü, ä, ö, ß
- Footer: `MARKE | SEO-Potenzialanalyse · DOMAIN`
- Closing: Kontakt m.weber@more-fire.com, kein Skill-Verweis
- Footer-Abstand: Inhalt muss mindestens 80px über dem unteren Rand enden
