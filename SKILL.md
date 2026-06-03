---
name: serp-competitive-analysis
description: >
  Analysiert Google- (und optional Bing-)SERPs für vorgegebene Keywords und erstellt eine vollständige Wettbewerbsanalyse: Wer rankt organisch in den Top 10? Wer schaltet Ads? Wie kommunizieren die Wettbewerber konkret — Hauptargument, Themen, Preise, Tonalität, Trust-Signale, Barrier-Handling, Persona-Abdeckung, Micro-Copy, Seitenaufbau? Abschließender Abgleich mit der eigenen Seite inkl. Gap-Analyse und Empfehlungen. Gedacht nicht nur für SEO, sondern als strategische Kommunikationsbasis für alle Marketingkanäle.

  Nutze diesen Skill IMMER wenn jemand sagt: "analysiere die SERPs für", "wer rankt für Keyword X", "Wettbewerbsanalyse für Keywords", "SERP-Analyse", "wie kommunizieren Wettbewerber bei Google", "was machen Konkurrenten bei Keyword X", "schau mal wer bei Google für X rankt", "SEO-Wettbewerbsanalyse", "wie positionieren sich Konkurrenten", "wie sprechen Wettbewerber die Nutzer an", oder wenn jemand eine URL/Marke zusammen mit einem Keyword und dem Wunsch nach Vergleich, Kommunikationsanalyse oder Positionierungscheck nennt — auch wenn die Worte "SERP" oder "Wettbewerb" nicht explizit fallen.
---

# SERP Competitive Analysis — Skill

Vollautomatisierte Wettbewerbsanalyse auf Basis von Live-SERP-Daten und Seitenanalysen via BrightData MCP. Ziel: verstehen, wie Wettbewerber für ein transaktionales Keyword kommunizieren — und was das für die eigene Seite und alle weiteren Marketingkanäle bedeutet.

Das Ergebnis ist keine reine SEO-Analyse, sondern eine Kommunikations- und Positionierungsgrundlage: Welche Botschaften, Personas, Tonalitäten und Conversion-Sprache dominieren das Keyword — und wo steht die eigene Seite dazu?

Output: HTML-Deck im morefire-Design → PDF-Export via Puppeteer. Templates unter `templates/`.

---

## Grundprinzip

Google zeigt in den SERPs bereits die "optimale Antwort" auf die Suchanfrage — rückwärts gelesen ergibt das, was Nutzer wirklich erwarten: welche Themen, welchen Ton, welche Seitenstruktur, welche Vertrauenssignale. Wer dort oben steht, hat diese User Story implizit richtig beantwortet. Die Analyse liest genau das heraus und gleicht es mit der eigenen Seite ab.

---

## Haltung des Reports

Lücken als Chancen formulieren, nicht als Vorwürfe. Wettbewerber sachlich beschreiben — was sie anders machen, nicht ob das besser ist. Findings konkret und belegbar: lieber "6 von 9 Wettbewerbern nennen einen Beispielpreis im Hero" als "Wettbewerber sind preistransparenter".

---

## Phase 1 — Briefing

Stelle alle folgenden Fragen auf einmal per AskUserQuestion, bevor du Daten abrufst:

1. **Eigene Marke & URL** — Welche Marke/URL als Referenz? (z.B. enerix / https://enerix.de)
2. **Keyword(s)** — Für welche Keywords soll analysiert werden? (Komma-getrennt)
3. **Suchmaschine** — Google (Standard) / Bing / Beides
4. **Zielmarkt/Sprache** — Standard: Deutschland / Deutsch. Nur abfragen wenn aus Keywords nicht erkennbar.
5. **Wettbewerber-Kategorien (optional)** — Eigene Gruppenbezeichnungen oder leer lassen für automatische Erkennung.
6. **Erweiterte Analyse? (optional)** — Funnel-Präsenz, SERP-Feature-Ownership, Ad-Landingpage-Konsistenz. Standard: Nein.

Falls Infos bereits im Gesprächsverlauf vorhanden: direkt verwenden.

---

## Phase 2 — SERP-Daten abrufen

**Bevorzugt:** BrightData Scraping Browser direkt auf Google navigieren, um vollständige SERP-Daten inkl. PAA, Related Searches und Ads-Details zu erhalten:
- Tool: `mcp__9ba7c41d-c96a-4371-ab3c-884dec2e38d1__scraping_browser_navigate` → `https://www.google.de/search?q=KEYWORD&hl=de&gl=de`
- Dann: `mcp__9ba7c41d-c96a-4371-ab3c-884dec2e38d1__scraping_browser_get_text` für den vollen SERP-Inhalt

**Fallback** (strukturierte Ergebnisse ohne PAA/Ads-Details):
- Tool: `mcp__9ba7c41d-c96a-4371-ab3c-884dec2e38d1__search_engine`

**Was aus dem SERP extrahieren:**

Organic Results (Top 10): Position, Titel, URL/Domain, Meta-Description/Snippet

Paid Ads (separat): Reihenfolge, Domain, Anzeigentitel, Anzeigentext, Sitelinks. Falls keine Ads: explizit notieren — Fehlen von Ads ist ein strategisches Signal.

SERP-Signale:
- **People Also Ask (PAA):** Alle sichtbaren Fragen — zeigen Barrieren und versteckte Erwartungen
- **Related Searches:** Themenbreite und Intentionsvielfalt
- **Featured Snippets / Knowledge Panel:** Inhalt und Format
- **Dominanter Seitentyp:** Was zeigt Google mehrheitlich? (Ratgeber, Produktseiten, Vergleiche, Rechner, Videos)

---

## Phase 3 — User Story & Personas ableiten

Aus PAA, Related Searches und SERP-Typ eine User Story synthetisieren:

> "Ich sehe [Herausforderung] und suche [Unterstützung], um [Ziel] zu erreichen — und will dabei [Unsicherheit] überwinden."

Dazu:
- **Journey-Phase:** Informationell / Kommerziell / Transaktional
- **Wissensstand:** Einsteiger / informierter Laie / Experte
- **Zentrale Barrieren:** Was hält typische Nutzer zurück?

**3–5 Persona-Cluster** ableiten: Alle suchen dasselbe Keyword, aber aus unterschiedlichen Ausgangssituationen. PAA-Fragen zeigen diese Vielfalt. Pro Persona: Name/Bezeichnung, Suchmotiv, Wissensstand, Hauptbedürfnis, größte Barriere.

---

## Phase 4 — Kategorisierung der organischen Rankings

| Kategorie | Typische Merkmale |
|---|---|
| **Direktwettbewerber** | Gleicher Service/Produkt, direkte Konkurrenz |
| **Hersteller** | Markenhersteller der zugrundeliegenden Technologie |
| **Vergleichsplattformen** | Aggregatoren, Portale, Vergleichsseiten |
| **Publisher / Media** | Redaktionelle Ratgeber, Tests, Magazinbeiträge |
| **Marktplätze / Handel** | Onlineshops, Händler |
| **Sonstige** | Nicht eindeutig zuordenbar |

Eigene URL separat markieren, falls sie rankt.

**Page-Type-Mismatch-Check:** Welcher Seitentyp dominiert die Top 10? Ist die eigene Seite von einem anderen Typ? Das ist ein struktureller Befund — kein Content-Gap, sondern ein strategisches Signal.

---

## Phase 5 — Seitenanalyse (pro Ranking + eigene URL)

**Tool (bevorzugt):** `mcp__9ba7c41d-c96a-4371-ab3c-884dec2e38d1__scrape_as_markdown`
**Fallback:** `mcp__9ba7c41d-c96a-4371-ab3c-884dec2e38d1__scraping_browser_snapshot`

Die URL aus dem SERP-Snippet abrufen (Landing Page, nicht Homepage). Eigene URL immer mit gleichem Raster analysieren.

**Analyse-Raster pro Eintrag:**

```
Domain: [domain.de] | Position: [X] | Kategorie: [...]

HAUPTARGUMENT / USP:
→ Kernbotschaft der Seite in einem Satz. Was steht im Hero?

WEITERE THEMEN & ARGUMENTE (3–7 Stichpunkte):
→ Weitere Argumente, Vorteile, Inhalte

TONALITÄT:
→ Ansprache: formal (Sie) / informal (Du) / unpersönlich
→ Grundstimmung: emotional-inspirierend / rational-sachlich / mischend
→ Adressierung: Experte-zu-Experte / zu-informiertem-Laien / zu-Einsteiger
→ Framing: Chance/Gewinn / Risiko/Vermeidung
→ Markenpersönlichkeit: 2–3 Adjektive

BARRIER-HANDLING:
→ Welche Hemmschwellen werden aktiv adressiert und wie?

PREISKOMMUNIKATION:
→ Preis genannt? Format (Startpreis / Beispielrechnung / Ersparnis-Framing / Rechner)
→ Referenzgrößen (kWp, €/Jahr, Amortisationszeit, ...)

TRUST-SIGNALE:
→ Reviews/Bewertungen (Anzahl, Plattform, Score), Zertifikate, Garantien,
   Referenzprojekte, Partnerlogos, Presse, Gütesiegel, Regionalität

MICRO-COPY:
→ Primärer Button-Text (exakt), Vertrauens-Zeile unter CTA, Social Proof in Micro-Copy,
   Urgency-Signale, Formular-Headline

PERSONA-ABDECKUNG:
→ Welche der abgeleiteten Personas werden gut / teilweise / kaum adressiert?

SEITENSTRUKTUR & ELEMENTE:
→ Textumfang: kurz / mittel / lang
→ First Screen: Was ist ohne Scrollen sichtbar?
→ Interaktive Elemente: Rechner / Konfigurator / Chat
→ Mediale Elemente: Videos / Infografiken / Prozessdarstellungen
→ Soziale Elemente: Testimonials / Fallstudien
```

---

## Phase 6 — Report als HTML-Deck erstellen

Nutze die Templates unter `templates/` um das Ergebnis als HTML-Deck im morefire-Design zu rendern. Design-Referenz: `templates/ONBOARDING.md` und `templates/_template.html`.

Deck-Struktur (Slides):
1. Cover (s-cover) — Keyword + Marke + Datum
2. Strategischer Hauptbefund (Page-Type-Mismatch oder wichtigster Finding)
3. Section-Divider I — "SERP und User Story"
4. SERP Top-10-Tabelle mit Kategorien-Badges
5. User Story + Persona-Cards (Ghost-Number-Variante)
6. Section-Divider II — "Direktvergleich"
7. Direktvergleich Top-3 vs. eigene Seite (Tabelle, 4 Spalten)
8. Direktvergleich Top-Wettbewerber pro Kategorie vs. eigene Seite
9. Section-Divider III — "Gap-Analyse"
10. Themen und Botschaften (find-rows: ok / warn / gap)
11. Preiskommunikation (Strategic Rows)
12. Tonalität und Micro-Copy (2-Spalten)
13. Trust-Signale und Barrier-Handling (Assessment Cards)
14. Section-Divider IV — "Empfehlungen"
15. Kurzfristig (Pillar-Cards)
16. Mittelfristig + Strategisch (2-Spalten)
17. Closing — Kontakt: m.weber@more-fire.com, kein Skill-Verweis

**Footer-Regel (wichtig):**
Jede Folie bekommt einen Footer mit dem folgenden Format:
```html
<div class="footer">
  <span>Kundenname | SERP-Wettbewerbsanalyse für "KEYWORD"</span>
  <img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-farbig.svg" alt="more-fire" />
</div>
```
Bei Section-Divider-Folien (s-section) das weiße Logo verwenden. "KEYWORD" immer durch das tatsächlich analysierte Keyword ersetzen (z.B. `für "photovoltaikanlage"`, `für "SEO Agentur"`).

**Footer-Abstand (wichtig):**
Der Footer sitzt `bottom: 56px`, der Content-Bereich hat `padding-bottom: 96px`. Jede Inhalts-Sektion muss mit `padding-bottom: 56px` oder `min-height:0` enden, damit kein Text in den Footer-Bereich hineinragt. Bei Tabellen und langen Listen die Zeilen reduzieren oder Schriftgröße anpassen, bevor die Folie überfüllt wird.

**PDF-Export:**
```bash
# Server starten (vom Deck-Ordner aus):
npx serve -l 4000 .

# Export (in neuem Terminal, Node muss im PATH sein):
node templates/export-pdf.mjs mein-deck/mein-deck.html
# Output: mein-deck/mein-deck.pdf (1920×1080, 2×)
```

---

## Gap-Analyse: Sendbar vs. Nicht sendbar

Wichtigste Unterscheidung in der Gap-Analyse:

- **Sendbar** = Thema/Argument könnte kommuniziert werden, tut es aber nicht oder zu schwach → Content-Entscheidung
- **Nicht sendbar (fehlende Eigenschaft)** = Kann nicht kommuniziert werden, weil die zugrundeliegende Eigenschaft beim eigenen Angebot fehlt → Produkt-/Angebotsfrage, kein Content-Problem

Diese Unterscheidung hilft dem Kunden, richtig zu priorisieren.

---

## Anhang: Erweiterte Analysen (nur wenn in Phase 1 gewünscht)

**Funnel-Präsenz:** Ranken Top-Wettbewerber auch bei informativen/vergleichenden Vorstufen-Keywords? Wer den Nutzer früher "anwärmt", hat beim Transaktions-Keyword einen Vertrauensvorsprung.

**SERP-Feature-Ownership:** Wer besitzt PAA-Felder, Featured Snippets, Bewertungssterne? Welche Features könnte die eigene Seite durch gezielte Maßnahmen gewinnen?

**Ad-Landingpage-Konsistenz:** Stimmt bei werbetreibenden Wettbewerbern die Anzeigenbotschaft mit der Landing Page überein? Inkonsistenzen sind Schwachstellen.

---

## Hinweise zur Ausführung

- Eigene Seite immer mit identischem Raster analysieren wie die Wettbewerber.
- Keyword-Set: Bei mehreren Keywords erst alle SERPs abrufen, Überschneidungen identifizieren.
- Konkretheit vor Vollständigkeit: Lieber 8 belegte Findings als 20 oberflächliche.
- Sprache des Reports: richtet sich nach der Keyword-Sprache.
- Copy-Regel: Keine Em-Dashes (—) im Deck-Text.
- Umlaut-Regel: Immer korrekte deutsche Umlaute verwenden (ü, ä, ö, ß). Niemals Ersetzungen wie ue, ae, oe, ss.
- Closing-Folie: Kontakt immer mit m.weber@more-fire.com. Kein Verweis auf den Skill oder das GitHub-Repository auf der Closing-Folie.
- Footer-Text: Immer `Kundenname | SERP-Wettbewerbsanalyse für "KEYWORD"` mit dem tatsächlichen Keyword in Anführungszeichen.
