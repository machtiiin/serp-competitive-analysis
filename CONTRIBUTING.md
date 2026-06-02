# Contributing

Dieser Skill kann von allen Teammitgliedern und autorisierten Partnern weiterentwickelt werden.

---

## Workflow

```
main        → stabiler Stand, getestete Analysen
dev         → aktive Entwicklung
feature/X   → neue Features oder Anpassungen
```

Keine direkten Pushes auf `main`. Änderungen via Pull Request, mindestens ein Review.

---

## Was erweitert werden kann

**SKILL.md**
- Neue Analyse-Dimensionen im Raster ergänzen
- Neue Report-Sektionen in der Deck-Struktur hinzufügen
- Andere Suchmaschinen oder Märkte (z.B. AT, CH) integrieren

**templates/**
- Design-Anpassungen in `deck-theme.css` (Farben, Typo)
- Neue Slide-Typen in `_template.html` ergänzen (immer auch in `ONBOARDING.md` dokumentieren)

**examples/**
- Neue Analyse-Beispiele als HTML + PDF beifügen
- Beispiele sollten unterschiedliche Branchen oder Keyword-Typen abdecken

---

## Design-Regeln

Vor Änderungen an Templates bitte `templates/ONBOARDING.md` lesen. Wichtigste Regeln:

- Keine Em-Dashes (--) im Slide-Text
- Keine Emojis
- Slide-Format: 1920x1080px
- Font: Heebo (Google Fonts)
- Farb-Variablen nicht hardcoden, immer `var(--c-red)` etc. verwenden

---

## Neue Analyse anlegen

```bash
# Im Repo-Root:
mkdir -p mein-projekt
cp templates/_template.html mein-projekt/mein-projekt.html

# Pfade anpassen (von ./ auf ../templates/):
# href="../templates/deck-theme.css"
# src="../templates/deck-stage.js"
# src="../templates/tweaks-panel.jsx"

# Server starten und bearbeiten:
npx serve -l 4000 .
# → http://localhost:4000/mein-projekt/mein-projekt.html

# PDF exportieren:
node templates/export-pdf.mjs mein-projekt/mein-projekt.html
```

---

## Fragen und Issues

GitHub Issues nutzen. Bei Fragen zum Design-System: morefire-Team kontaktieren.
