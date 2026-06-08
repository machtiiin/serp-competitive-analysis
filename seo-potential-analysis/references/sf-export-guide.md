# ScreamingFrog + GSC Export-Anleitung

## ScreamingFrog — Internal HTML Export

1. Crawl vollständig durchlaufen lassen
2. Linke Seitenleiste: **Internal** wählen
3. Filter oben: **HTML** (nur HTML-Seiten, keine Bilder/CSS/JS)
4. **Bulk Export → Internal → HTML** → Export as CSV

**Wichtige Spalten (müssen aktiviert sein):**
- Address (URL) — immer vorhanden
- Status Code — immer vorhanden
- Indexability — Configuration → Spider → Crawl → "Follow Robots"
- Title 1 + Title Count
- H1-1 + H1-Count
- Word Count — **Configuration → Spider → Extraction → Store Text**

**Für Q*-Analyse mit Text-Extraktion:**
- Configuration → Custom Extraction → XPath/CSS/RegEx für Hauptinhalt
- Nach Crawl: Bulk Export → Custom Extraction → Export as CSV

---

## Google Search Console — Seiten-Export

1. Search Console öffnen → **Leistung**
2. Zeitraum: **Letzte 3 Monate** (oder bis 16 Monate)
3. Tab: **Seiten** (nicht Suchanfragen)
4. Klicks, Impressionen, CTR, Position eingeblendet lassen
5. Export-Symbol → **CSV herunterladen**

**Erwartete Spalten:** Seite, Klicks, Impressionen, CTR, Position

---

## Typische Probleme

| Problem | Lösung |
|---|---|
| Word Count fehlt | SF → Configuration → Spider → Extraction → Store Text aktivieren, neu crawlen |
| Spalte "Indexability" fehlt | SF → Configuration → Spider → Crawl → Robots aktivieren |
| GSC zeigt nur 1.000 Zeilen | GSC kann max. 1.000 Zeilen per CSV exportieren; für mehr: Data Studio nutzen |
| URL-Mismatch SF vs. GSC | Beide müssen HTTPS und gleiche Domain-Variante nutzen (mit/ohne www) |
| Fehler "Spalte nicht gefunden" | Export-Sprache prüfen: Script erkennt DE und EN Spaltennamen automatisch |
