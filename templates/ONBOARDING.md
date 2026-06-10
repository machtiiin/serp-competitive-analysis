# Slides Design Reference

Kurzreferenz für das HTML-Deck-System. Immer zuerst lesen, bevor Slides gebaut oder geändert werden.

---

## Slide-Klassen

### Hintergründe
```
s-cover        → roter Vollbild-Cover (Titelfolie)
s-section      → schwarzer Section-Divider
s-grey         → hellgrauer Hintergrund (z. B. Closing)
(default)      → weißer Hintergrund
```

### Layout
```
frame          → Standard-Inhaltsfolie mit Padding + Footer-Slot
frame-flush    → kein Innen-Padding (für Cover/Divider)
frame-centered → Inhalt vertikal zentriert (mit frame-header + frame-body)
cols-2         → 2-Spalten-Grid
cols-3         → 3-Spalten-Grid
cols-4         → 4-Spalten-Grid
```

### Typografie
```
.display       → große Hero-Überschrift
.title         → Folientitel (h1)
.lead          → Unter-Titelzeile (größer, gedämpft)
.body          → Fließtext
.eyebrow       → Kategorie-Label oben links (Uppercase, klein)
.bignum        → riesige Ziffer für Section-Divider
.ch-stat       → große Statistik-Zahl  →  <p class="ch-stat">24<span class="unit">%</span></p>
.mono          → Monospace-Inline (für URLs, Code, Tags)
```

### Komponenten
```
.pillar-card   → Karte mit tag + h3 + p  (border, padding, flex-col)
.find-row      → Zeile mit Icon + Label + Pill  (für Checklisten)
.check-row     → Variante von find-row
.chip          → Inline-Badge (URL, Keyword)  →  <span class="chip">beispiel.de</span>
.chip.bad      → roter Chip
.chip.dark     → dunkler Chip
.robots-block  → Monospace-Code-Block (robots.txt, JSON-LD)
.clean         → Liste ohne Bullets  →  <ul class="clean"><li><span class="idx">01</span><span class="lab">Text</span></li></ul>
```

### Pills (Status-Badges in find-row)
```
<div class="pill gap">Fix</div>      → rot
<div class="pill warn">Review</div>  → orange
<div class="pill ok">OK</div>        → grün
```

### CSS-Variablen
```
--c-red        → Akzentfarbe (Standard: #DB3543)
--c-orange     → Sekundärfarbe (#f08262)
--c-green      → Grün für OK-Status
--c-black      → #1d1d1b
--c-grey       → Hellgrau (Karten-Hintergrund)
--c-ink-60     → Gedämpfter Text (60% Schwarz)
--c-ink-40     → Noch gedämpfter
--c-ink-15     → Trennlinien
--pad-x        → Horizontales Seiten-Padding
```

---

## Status-Icons (SVG, inline in find-row)

### Rot (Fehler / Fix)
```html
<svg viewBox="0 0 24 24" fill="none" class="ico">
  <circle cx="12" cy="12" r="10" fill="var(--c-red)"/>
  <path d="M8 8 L16 16 M16 8 L8 16" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
</svg>
```

### Orange (Warnung / Review)
```html
<svg viewBox="0 0 24 24" fill="none" class="ico">
  <circle cx="12" cy="12" r="10" fill="var(--c-orange)"/>
  <line x1="8" y1="12" x2="16" y2="12" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>
</svg>
```

### Grün (OK)
```html
<svg viewBox="0 0 24 24" fill="none" class="ico">
  <circle cx="12" cy="12" r="10" fill="var(--c-green)"/>
  <path d="M8 12.5 L11 15.5 L16.5 9.5" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
```

---

## Context Note (über Footer, eine Zeile)
```html
<div class="context-note">
  <svg width="20" height="20" viewBox="0 0 22 22" fill="none" style="flex-shrink:0; color:var(--c-red);">
    <circle cx="11" cy="11" r="10" stroke="currentColor" stroke-width="1.5"/>
    <path d="M11 10v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="11" cy="7" r="1" fill="currentColor"/>
  </svg>
  <span class="context-label">Kontext</span>
  <span class="context-text">Einzeiliger Hinweis.</span>
</div>
```

---

## Typische Slide-Strukturen

### Find-Row-Checkliste (technische Analyse)
```html
<section data-screen-label="XX Titel" class="frame">
  <div class="eyebrow">SECTION NAME</div>
  <h1 class="title">Slide-Titel</h1>
  <p class="lead" style="margin-top:4px; color:var(--c-ink-60);">Lead-Satz.</p>
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
    <div class="find-row">
      <!-- icon --> <div><div class="label-title">Titel</div><div class="label-desc">Beschreibung</div></div>
      <div class="pill gap">Fix</div>
    </div>
    <!-- weitere find-rows, letzte ohne border-bottom -->
  </div>
  <div class="footer"><span>Client | Deck-Titel</span><img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-farbig.svg" alt="more-fire" /></div>
</section>
```

### Section-Divider
```html
<section data-screen-label="XX Section" class="s-section frame-flush"
         style="display:flex; align-items:center; justify-content:flex-start; padding:0 var(--pad-x);">
  <div style="display:grid; grid-template-columns:auto 1fr; gap:80px; align-items:center; width:100%;">
    <div class="bignum" style="color:var(--c-red);">I</div>
    <div>
      <div style="font-size:24px; color:var(--c-orange); font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:24px;">LABEL</div>
      <h1 class="display" style="color:#fff; font-size:120px; max-width:14ch;">Titel.</h1>
      <p style="font-size:30px; color:rgba(255,255,255,.7); font-weight:300; line-height:1.35; margin:32px 0 0; max-width:44ch;">Beschreibung.</p>
    </div>
  </div>
  <div class="footer">
    <span style="color:rgba(255,255,255,.5);">Client | Deck-Titel</span>
    <img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-white.svg" alt="more-fire" />
  </div>
</section>
```

### Stats-Slide (ch-stat)
```html
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:32px; margin-top:40px;">
  <div style="display:flex; flex-direction:column; gap:8px;">
    <p class="ch-stat">42.393</p>
    <div style="font-size:22px; color:var(--c-ink-60); font-weight:500; line-height:1.3;">Beschreibung</div>
  </div>
</div>
```

---

## Lead-Text (Inhalts-Einleitung)

Grauer Einleitungstext unter dem Titel auf INHALTE-Folien. Kein eigener CSS-Klasse — inline:

```html
<p style="font-size:26px; color:var(--c-ink-60); font-weight:300; line-height:1.4; margin:0 0 28px;">
  Einleitungstext, der das Thema der Folie in 1-2 Sätzen einordnet.
</p>
```

---

## Assessment Cards (Kundenspezifische Bewertung)

Für INHALTE-Folien, die ein Konzept links erklären und rechts den Kunden bewerten.
Icons: 32×32 viewBox (größer als find-row), Inline-Status-Badge in derselben Titelzeile.

```html
<!-- Wrapper rechte Spalte -->
<div style="display:flex; flex-direction:column; gap:10px;">
  <div style="font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:var(--c-ink-40); margin-bottom:2px;">BEWERTUNG KUNDE.DE</div>

  <!-- Grün: Vorhanden -->
  <div style="display:flex; align-items:flex-start; gap:16px; padding:14px 18px; border:1px solid var(--c-ink-15); border-radius:10px;">
    <svg width="22" height="22" viewBox="0 0 32 32" fill="none" style="flex-shrink:0; margin-top:2px;">
      <circle cx="16" cy="16" r="16" fill="var(--c-green)"/>
      <path d="M9 16L13.5 20.5L23 11" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div>
      <div style="font-size:17px; font-weight:700; color:var(--c-black); line-height:1.2;">Begriff <span style="font-weight:400; color:var(--c-green); font-size:14px; letter-spacing:0.06em; text-transform:uppercase; margin-left:6px;">Vorhanden</span></div>
      <div style="font-size:14px; color:var(--c-ink-60); margin-top:4px; line-height:1.4;">Kundenspezifischer Befund.</div>
    </div>
  </div>

  <!-- Orange: Teilweise / Ausbaufähig -->
  <div style="display:flex; align-items:flex-start; gap:16px; padding:14px 18px; border:1px solid var(--c-ink-15); border-radius:10px;">
    <svg width="22" height="22" viewBox="0 0 32 32" fill="none" style="flex-shrink:0; margin-top:2px;">
      <circle cx="16" cy="16" r="16" fill="var(--c-orange)"/>
      <path d="M16 10v7" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="16" cy="21" r="1.5" fill="white"/>
    </svg>
    <div>
      <div style="font-size:17px; font-weight:700; color:var(--c-black); line-height:1.2;">Begriff <span style="font-weight:400; color:var(--c-orange); font-size:14px; letter-spacing:0.06em; text-transform:uppercase; margin-left:6px;">Teilweise</span></div>
      <div style="font-size:14px; color:var(--c-ink-60); margin-top:4px; line-height:1.4;">Kundenspezifischer Befund.</div>
    </div>
  </div>

  <!-- Rot: Fehlt / Nicht vorhanden -->
  <div style="display:flex; align-items:flex-start; gap:16px; padding:14px 18px; border:1px solid var(--c-ink-15); border-radius:10px;">
    <svg width="22" height="22" viewBox="0 0 32 32" fill="none" style="flex-shrink:0; margin-top:2px;">
      <circle cx="16" cy="16" r="16" fill="var(--c-red)"/>
      <path d="M10 10L22 22M22 10L10 22" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
    </svg>
    <div>
      <div style="font-size:17px; font-weight:700; color:var(--c-black); line-height:1.2;">Begriff <span style="font-weight:400; color:var(--c-red); font-size:14px; letter-spacing:0.06em; text-transform:uppercase; margin-left:6px;">Fehlt</span></div>
      <div style="font-size:14px; color:var(--c-ink-60); margin-top:4px; line-height:1.4;">Kundenspezifischer Befund.</div>
    </div>
  </div>
</div>
```

Mögliche Status-Werte: `Vorhanden` (grün) · `Teilweise` (orange) · `Ausbaufähig` (orange) · `Kaum vorhanden` (rot) · `Nicht vorhanden` (rot) · `Fehlt` (rot)

---

## Chapter Reference Hint (Verweis auf andere Folie)

Hinweis-Element direkt unter einem Label, um auf die Herkunft der Daten hinzuweisen.
Wird auf Inhalts-Folien verwendet, die Daten aus einem anderen Kapitel wiederholen.

```html
<div style="display:inline-flex; align-items:center; gap:10px; margin-top:8px; margin-bottom:16px;
     border-left:3px solid var(--c-red); padding:8px 14px 8px 12px;
     background:rgba(0,0,0,0.04); border-radius:0 6px 6px 0;">
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style="flex-shrink:0; color:var(--c-red);">
    <path d="M8 3L13 8L8 13M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span style="font-size:14px; color:var(--c-ink-60);">Aus Kapitel <strong style="color:var(--c-black);">02 · Aktuelle KI-Sichtbarkeit</strong>, Folie 13</span>
</div>
```

---

## Contrast Card Pair (Hell/Dunkel gestapelt)

Zwei übereinander gestapelte Karten zum Kontrast (z.B. generisch vs. einzigartig, alltäglich vs. nicht-alltäglich).

```html
<div style="display:flex; flex-direction:column; gap:12px;">
  <!-- Helle Karte (negatives Beispiel) -->
  <div style="background:#f5f5f5; border-radius:12px; padding:20px 24px;">
    <div style="font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--c-ink-40); margin-bottom:10px;">Alltäglich</div>
    <div style="display:flex; flex-direction:column; gap:6px;">
      <div style="display:flex; gap:10px; align-items:flex-start; font-size:15px; color:var(--c-ink-60);">
        <span style="color:var(--c-red); margin-top:2px;">✗</span>Generischer Bullet-Point
      </div>
    </div>
    <div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(0,0,0,0.1); font-size:13px; font-weight:700; color:var(--c-red); letter-spacing:0.06em; text-transform:uppercase;">KI braucht diese Seite nicht.</div>
  </div>

  <!-- Dunkle Karte (positives Beispiel) -->
  <div style="background:var(--c-black); border-radius:12px; padding:20px 24px;">
    <div style="font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:rgba(255,255,255,.4); margin-bottom:10px;">Nicht-alltäglich</div>
    <div style="display:flex; flex-direction:column; gap:6px;">
      <div style="display:flex; gap:10px; align-items:flex-start; font-size:15px; color:rgba(255,255,255,.8);">
        <span style="color:#6dd49a; margin-top:2px;">✓</span>Einzigartiger Bullet-Point
      </div>
    </div>
    <div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,.12); font-size:13px; font-weight:700; color:#6dd49a; letter-spacing:0.06em; text-transform:uppercase;">KI zitiert diese Seite aktiv.</div>
  </div>
</div>
```

---

## Strategic Evaluation Rows (Strategie-Bewertung)

Für Folien, die ein Framework (z.B. 4 Strategien) gegen den Kundenstatus abgleichen.
Container: 90% Breite, zentriert. Grid pro Reihe: `280px 1fr 260px`.

```html
<div style="flex:1; display:flex; flex-direction:column; gap:12px; min-height:0; padding-bottom:56px; max-width:90%; margin:0 auto; width:90%;">

  <div style="display:grid; grid-template-columns:280px 1fr 260px; border:1px solid var(--c-ink-15); border-radius:10px; overflow:hidden; flex:1;">
    <!-- Linke Zelle: Strategie-Label -->
    <div style="background:#f7f7f7; padding:16px 20px; border-right:1px solid var(--c-ink-15); display:flex; flex-direction:column; justify-content:center; gap:4px;">
      <div style="font-size:11px; font-weight:700; color:var(--c-red); text-transform:uppercase; letter-spacing:0.08em;">01</div>
      <div style="font-size:18px; font-weight:700; line-height:1.2;">Strategie-Name</div>
      <div style="font-size:13px; color:var(--c-ink-60); line-height:1.3;">Kurzbeschreibung der Strategie</div>
    </div>
    <!-- Mittlere Zelle: Kundenspezifischer Befund -->
    <div style="padding:16px 22px; display:flex; flex-direction:column; justify-content:center; gap:6px;">
      <div style="font-size:15px; color:var(--c-ink-60); line-height:1.45;">Kundenspezifischer Befund.</div>
      <div style="font-size:14px; color:var(--c-black); font-weight:700;">Opportunity: Konkrete Empfehlung.</div>
    </div>
    <!-- Rechte Zelle: Status (orange=#fff8f0 / rot=#fff5f5) -->
    <div style="background:#fff8f0; padding:16px 20px; border-left:1px solid var(--c-ink-15); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px;">
      <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
        <circle cx="16" cy="16" r="16" fill="var(--c-orange)"/>
        <path d="M16 10v7" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="16" cy="21" r="1.5" fill="white"/>
      </svg>
      <div style="font-size:13px; font-weight:700; color:var(--c-orange); text-transform:uppercase; letter-spacing:0.08em; text-align:center;">Teilweise</div>
    </div>
  </div>

</div>
```

Hintergrundfarben Rechte Zelle: Orange: `#fff8f0` · Rot: `#fff5f5` · Grün: `#f0fdf4`

---

## SVG-Chart Favicons (X-Achse)

Favicons unterhalb von Domain-Labels in SVG-Balkendiagrammen.

```html
<!-- 1. viewBox auf 540 erweitern (statt 500) -->
<svg viewBox="0 0 1600 540" ...>
  <defs>
    <!-- 2. Kreisförmiger Clip pro Domain -->
    <clipPath id="fav-domain"><circle cx="255" cy="464" r="11"/></clipPath>
  </defs>

  <!-- 3. Hintergrundkreis + Favicon + Text -->
  <circle cx="255" cy="464" r="12" fill="#f5f5f5"/>  <!-- eigene Domain: fill="#fff0f1" -->
  <image href="https://www.google.com/s2/favicons?domain=example.de&sz=32"
         x="244" y="453" width="22" height="22" clip-path="url(#fav-domain)"/>
  <text x="255" y="492" font-size="14" text-anchor="middle" ...>example.de</text>
</svg>
```

Reihenfolge: Favicon-Kreis → URL-Text (Favicon über Text, ~8px Abstand).
Eigene Domain: Hintergrundkreis `#fff0f1`, alle anderen `#f5f5f5`.

---

> **Neues Deck anlegen & Copy-Regeln:** siehe `CLAUDE.md` (Regeln) bzw. `README.md` (Anleitung).
