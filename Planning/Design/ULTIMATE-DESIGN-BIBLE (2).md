# ULTIMATE DESIGN BIBLE
## The Complete Framework for Building World-Class Digital Products

> Every principle, pattern, rule, and system you need to build interfaces that feel
> like Stripe, Linear, Vercel, Notion, and Apple — from scratch, on any stack.

---

# TABLE OF CONTENTS

| Part | Topic |
|---|---|
| 1 | Design Philosophy & Inspirations |
| 2 | Universal Design Laws |
| 3 | Color System |
| 4 | Typography System |
| 5 | Spacing System |
| 6 | Layout Architecture |
| 7 | Component Blueprint |
| 8 | Premium Effects System |
| 9 | Animation System |
| 10 | Authentication Design |
| 11 | Dashboard Architecture |
| 12 | AI SaaS & Modern 2026 Design |
| 13 | Mobile-First Rules |
| 14 | Accessibility System |
| 15 | Performance Design Rules |
| 16 | Design Psychology |
| 17 | Design Audit Checklist |
| 18 | Page Templates |
| 19 | SaaS Templates |
| 20 | Enterprise Templates |
| 21 | Personal Project Blueprint |

---

# PART 1 — DESIGN PHILOSOPHY & INSPIRATIONS

## 1.1 STRIPE DESIGN PRINCIPLES

Stripe is the gold standard for developer-facing SaaS. Their interface communicates trust, precision, and technical credibility.

- **Clarity over cleverness.** Every element has a reason to exist. Nothing is decorative.
- **Density without clutter.** Consistent spacing, strong typographic hierarchy, restrained color.
- **Borders over shadows.** `1px solid #e3e8ef` for card separation instead of box-shadows. Flat, precise, technical.
- **Micro-copy is design.** Button labels, error messages, and placeholder text are written with the same care as marketing copy.
- **Ghost-to-fill buttons.** Outlined at rest, filled on hover. The most trusted CTA pattern in SaaS.
- **Whitespace is the design.** 80–120px section padding. 32–48px between components.

**Patterns to steal:** Ghost buttons, inline validation, monospace for data values, subtle grid lines on tables, generous whitespace.

---

## 1.2 LINEAR DESIGN PRINCIPLES

Linear is the benchmark for modern productivity tool design. Dark-first, keyboard-first, speed-first.

- **Speed is a feature.** Every interaction is instant. Animations are 150–200ms maximum.
- **Dark mode is the default.** `#0F0F0F` background, `#1A1A1A` cards.
- **Monochromatic + one accent.** Entire interface is grayscale with a single purple accent.
- **Left accent border for active states.** `border-left: 2px solid accent` — a Linear invention every SaaS now copies.
- **Command palette (⌘K).** Primary navigation method. Every action has a keyboard shortcut.

**Linear's color system:** `--bg: #0F0F0F`, `--surface: #1A1A1A`, `--border: rgba(255,255,255,0.08)`, `--accent: #5E6AD2`. Four values. That's the entire system.

---

## 1.3 VERCEL DESIGN PRINCIPLES

Vercel's design is the purest expression of "developer aesthetic" — black, white, and nothing else.

- **Black and white only.** Zero color except semantic states (green success, red error).
- **Borders, not shadows.** `1px solid` for separation. Precise, technical feel.
- **Monospace for everything technical.** Deployment IDs, commit hashes, env vars — all monospace.
- **Instant feedback.** Every action has immediate visual feedback.
- **Progressive disclosure.** Advanced settings hidden behind "Advanced" toggles.

**Vercel's button:** `background: #000; color: #fff; border-radius: 6px; padding: 8px 16px; font-weight: 500`. No gradient. No shadow. Pure contrast.

---

## 1.4 NOTION DESIGN PRINCIPLES

Notion is the master of "calm design" — an interface that gets out of the way.

- **Content is the UI.** Toolbars appear on hover, not permanently.
- **Generous line height.** `line-height: 1.7–2.0` for body text. More than any other product.
- **Hover-reveal interactions.** Drag handles, action buttons appear only on hover.
- **Three-layer shadow** for depth:

```css
box-shadow:
  rgba(15,15,15,0.05) 0px 0px 0px 1px,
  rgba(15,15,15,0.10) 0px 3px 6px,
  rgba(15,15,15,0.20) 0px 9px 24px;
```

---

## 1.5 APPLE HUMAN INTERFACE PRINCIPLES

- **Clarity.** Text is legible at every size. Icons are precise. Adornments are subtle.
- **Deference.** The UI helps people understand content but never competes with it.
- **Depth.** Visual layers and realistic motion convey hierarchy.
- **Feedback.** Every action has a response. Acknowledge input immediately.
- **Minimum touch target: 44×44pt.**
- **Apple's blur/glass pattern:**

```css
background: rgba(255, 255, 255, 0.72);
backdrop-filter: saturate(180%) blur(20px);
-webkit-backdrop-filter: saturate(180%) blur(20px);
border: 1px solid rgba(255, 255, 255, 0.3);
```

---

## 1.6 SYNTHESIZED DESIGN PHILOSOPHY

| Principle | Source | Application |
|---|---|---|
| Whitespace is the design | Stripe | 60–96px section padding |
| Speed is a feature | Linear | 150–250ms all transitions |
| Black/white first, color second | Vercel | Monochromatic base + one accent |
| Content over chrome | Notion | Hover-reveal UI, minimal toolbars |
| Feedback for every action | Apple | Loading, success, error states |
| Borders over shadows | Stripe + Vercel | `1px solid` for separation |
| Left border = active | Linear | Selected state pattern |
| Blur for depth | Apple | Glassmorphism overlays |
| Typography does the work | All five | Weight + size hierarchy before color |

---

# PART 2 — UNIVERSAL DESIGN LAWS

**Law 1:** One dominant element per screen. If everything is loud, nothing is heard.
**Law 2:** Three levels of hierarchy — hero, section, content. Never more.
**Law 3:** Size communicates importance, not decoration.
**Law 4:** Dark, saturated colors carry more visual weight. Use them for headings only.
**Law 5:** Whitespace is structure. Small gap = related. Large gap = new section.
**Law 6:** Eye moves left-to-right, top-to-bottom. Place CTAs at the end of the reading flow.
**Law 7:** The highest-contrast element gets looked at first. Make it your primary CTA.
**Law 8:** Base-8 grid. All values are multiples of 8: 8, 16, 24, 32, 40, 48, 64, 80, 96.
**Law 9:** Section padding > component padding > element padding. Never the same value at different levels.
**Law 10:** Consistent internal padding within a component type. Inconsistency signals carelessness.
**Law 11:** Fixed navbar requires content offset = navbar height + 8–16px buffer.
**Law 12:** Use padding on containers, not margin on last children.
**Law 13:** Minimum 16–20px horizontal padding on all containers.
**Law 14:** Two fonts maximum. Display (Poppins/Inter) + Body (Roboto/Inter).
**Law 15:** Font weight signals hierarchy more than font size. Use weight first.
**Law 16:** Body text: 15–17px. Below 14px is inaccessible. Above 18px is a heading.
**Law 17:** Body line-height: 1.5–1.7. Heading line-height: 1.1–1.3.
**Law 18:** Large headings (2rem+) need `letter-spacing: -0.01em to -0.03em`.
**Law 19:** Muted text = lighter gray or reduced opacity. Never a different hue.
**Law 20:** Uppercase only for labels and badges. Never for body text.
**Law 21:** One primary. One secondary. One accent. More creates noise.
**Law 22:** Primary saturation: 80–100%. Brightness: 40–60%.
**Law 23:** Semantic colors are sacred. Red=error. Green=success. Amber=warning. Blue=info.
**Law 24:** Backgrounds: near-zero saturation. Colored backgrounds compete with content.
**Law 25:** Warm-to-white gradient beats flat white. `linear-gradient(to right, #ece9e6, #fff)`.
**Law 26:** Dark surfaces: semi-transparent, not solid black. `rgba(0,0,0,0.8)` not `#000`.
**Law 27:** Color is never the only differentiator. Always add a second signal.
**Law 28:** Three button variants: primary, secondary, ghost. More creates decision paralysis.
**Law 29:** Button height standardized: sm=32px, md=44px, lg=52px.
**Law 30:** All cards on a page use the same resting shadow.
**Law 31:** Card hover shadow doubles the resting shadow. Y-offset and blur both increase.
**Law 32:** Left border accent = selected/active state. `border-left: 3px solid primary`.
**Law 33:** Inputs: default border → focus border + glow → error border + red text.
**Law 34:** Focus rings must be visible and branded. Never just `outline: none`.
**Law 35:** Hover: 150–250ms. Modal: 200–300ms. Page: 300–500ms. Scroll reveal: 400–600ms.
**Law 36:** `ease-out` for entrances. `ease-in` for exits. Never `linear` for UI.
**Law 37:** Animate `transform` and `opacity` only. Never `width`, `height`, `top`, `left`.
**Law 38:** Maximum two properties animated simultaneously on hover.
**Law 39:** Stagger list animations by 50–100ms per item.
**Law 40:** Always respect `prefers-reduced-motion`.
**Law 41:** Minimum contrast: 4.5:1 normal text, 3:1 large text (WCAG AA).
**Law 42:** Every interactive element needs a visible focus state.
**Law 43:** Touch targets: minimum 44×44px.
**Law 44:** Labels always visible. Never placeholder-only.
**Law 45:** `aria-live` for all dynamic content updates.

---

# PART 3 — COLOR SYSTEM

```css
:root {
  /* PRIMARY */
  --color-primary:         hsl(211, 100%, 50%);
  --color-primary-dark:    hsl(211, 100%, 35%);
  --color-primary-light:   hsl(211, 100%, 96%);
  --color-primary-alpha:   rgba(0, 123, 255, 0.15);
  --color-primary-ring:    rgba(0, 123, 255, 0.45);

  /* SECONDARY */
  --color-secondary:       hsl(208, 7%, 46%);
  --color-secondary-dark:  hsl(208, 7%, 31%);
  --color-secondary-light: hsl(210, 14%, 93%);

  /* ACCENT */
  --color-accent:          hsl(16, 100%, 66%);
  --color-accent-dark:     hsl(16, 100%, 50%);

  /* SURFACES */
  --color-surface-page:        #ffffff;
  --color-surface-warm:        #ece9e6;
  --color-surface-subtle:      #f8f9fa;
  --color-surface-card:        #ffffff;
  --color-surface-card-subtle: #f5f5f5;
  --color-surface-hover:       #e9ecef;
  --color-surface-selected:    #f0f7ff;
  --color-surface-input:       #ffffff;
  --gradient-body: linear-gradient(to right, #ece9e6, #ffffff);

  /* SEMANTIC */
  --color-success:        hsl(122, 39%, 49%);
  --color-success-dark:   hsl(123, 40%, 35%);
  --color-success-light:  hsl(88, 57%, 94%);
  --color-success-alpha:  rgba(76, 175, 80, 0.15);
  --color-warning:        hsl(38, 100%, 50%);
  --color-warning-dark:   hsl(38, 100%, 38%);
  --color-warning-light:  hsl(38, 100%, 95%);
  --color-error:          hsl(6, 78%, 57%);
  --color-error-dark:     hsl(6, 78%, 42%);
  --color-error-light:    hsl(6, 78%, 96%);
  --color-error-alpha:    rgba(231, 76, 60, 0.15);
  --color-info:           hsl(211, 100%, 50%);
  --color-info-light:     hsl(211, 100%, 96%);

  /* TEXT */
  --color-text-primary:   #333333;
  --color-text-secondary: #6c757d;
  --color-text-muted:     #adb5bd;
  --color-text-label:     #495057;
  --color-text-heading:   #343a40;
  --color-text-inverse:   #ffffff;

  /* BORDERS */
  --color-border-default: #dee2e6;
  --color-border-subtle:  #e9ecef;
  --color-border-strong:  #adb5bd;
  --color-border-focus:   hsl(212, 72%, 45%);

  /* OVERLAYS */
  --color-overlay-dark:   rgba(0, 0, 0, 0.80);
  --color-overlay-medium: rgba(0, 0, 0, 0.50);
  --color-overlay-light:  rgba(0, 0, 0, 0.05);

  /* DARK THEME */
  --color-dark-bg:        #0F0F0F;
  --color-dark-surface:   #1A1A1A;
  --color-dark-border:    rgba(255, 255, 255, 0.08);
  --color-dark-text:      rgba(255, 255, 255, 0.90);
  --color-dark-muted:     rgba(255, 255, 255, 0.45);

  /* GRADIENTS */
  --gradient-hero-blue:   linear-gradient(45deg, hsl(211,100%,50%), hsl(208,7%,46%));
  --gradient-hero-dark:   linear-gradient(135deg, #1a1a2e, #16213e);
  --gradient-hero-purple: linear-gradient(135deg, #667eea, #764ba2);
  --gradient-card-depth:  linear-gradient(145deg, #ffffff, #f5f5f5);
  --gradient-mesh: radial-gradient(at 40% 20%, hsl(228,100%,74%) 0px, transparent 50%),
                   radial-gradient(at 80% 0%,  hsl(189,100%,56%) 0px, transparent 50%),
                   radial-gradient(at 0%  50%, hsl(355,100%,93%) 0px, transparent 50%);
}
```

---

# PART 4 — TYPOGRAPHY SYSTEM

```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap');

html { font-size: 16px; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
body { font-family: "Roboto", "Inter", Arial, sans-serif; font-size: 1rem; font-weight: 400; line-height: 1.6; color: var(--color-text-primary); }

.text-display        { font-family:'Poppins',sans-serif; font-size:clamp(2rem,5vw,3rem); font-weight:700; line-height:1.1; letter-spacing:-0.02em; color:var(--color-text-inverse); text-shadow:2px 2px 5px rgba(0,0,0,0.25); }
.text-section-heading{ font-family:'Poppins',sans-serif; font-size:clamp(1.5rem,3vw,2rem); font-weight:600; line-height:1.25; letter-spacing:-0.01em; color:var(--color-text-heading); }
.text-card-heading   { font-family:'Poppins',sans-serif; font-size:1.25rem; font-weight:600; line-height:1.3; color:var(--color-text-primary); }
.text-subsection     { font-size:1.1rem; font-weight:600; line-height:1.4; color:var(--color-text-primary); }
.text-body-lg        { font-size:1.125rem; line-height:1.7; }
.text-body           { font-size:1rem; line-height:1.6; }
.text-body-sm        { font-size:0.9375rem; line-height:1.5; }
.text-supporting     { font-size:1rem; color:var(--color-text-secondary); line-height:1.5; }
.text-label          { font-size:0.875rem; font-weight:500; color:var(--color-text-label); }
.text-caption        { font-size:0.8125rem; color:var(--color-text-muted); }
.text-badge          { font-size:0.75rem; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; }
.text-mono           { font-family:'JetBrains Mono','Fira Code','Courier New',monospace; font-size:0.875rem; }
.text-kpi-value      { font-size:2rem; font-weight:700; line-height:1.1; letter-spacing:-0.02em; }

@media (max-width: 768px) {
  .text-display         { font-size: 2rem; }
  .text-section-heading { font-size: 1.5rem; }
  .text-card-heading    { font-size: 1.125rem; }
  .text-kpi-value       { font-size: 1.5rem; }
}
```

---

# PART 5 — SPACING SYSTEM

```css
:root {
  --space-1:  4px;  --space-2:  8px;  --space-3: 12px;
  --space-4: 16px;  --space-5: 20px;  --space-6: 24px;
  --space-7: 32px;  --space-8: 40px;  --space-9: 48px;
  --space-10:64px;  --space-11:80px;  --space-12:96px;
}
```

| Context | Token |
|---|---|
| Icon-to-text gap | `--space-2` (8px) |
| Input padding | `--space-3/4` (12–16px) |
| Button padding | `--space-3/6` (12px / 24px) |
| Card padding | `--space-5/6` (20–24px) |
| Grid gap | `--space-5/6` (20–24px) |
| Form field gap | `--space-4/6` (16–24px) |
| Section title margin | `--space-7/8` (32–40px) |
| Section padding | `--space-10/11` (64–80px) |
| Hero padding | `--space-11/12` (80–96px) |
| Navbar offset | `--space-10` (64px) |

---

# PART 6 — LAYOUT ARCHITECTURE

```css
.container-narrow  { max-width:680px;  margin:0 auto; padding:0 20px; }
.container-default { max-width:960px;  margin:0 auto; padding:0 20px; }
.container-wide    { max-width:1200px; margin:0 auto; padding:0 20px; }
.container-hero    { max-width:900px;  margin:0 auto; padding:0 20px; }

/* AUTO-FIT CARD GRID */
.grid-cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:var(--space-6); }

/* BENTO GRID */
.grid-bento { display:grid; grid-template-columns:repeat(12,1fr); grid-auto-rows:minmax(120px,auto); gap:var(--space-4); }
.bento-span-4  { grid-column:span 4; }
.bento-span-6  { grid-column:span 6; }
.bento-span-8  { grid-column:span 8; }
.bento-span-12 { grid-column:span 12; }
.bento-row-2   { grid-row:span 2; }

/* TOOL LAYOUT */
.layout-tool { display:grid; grid-template-columns:280px 1fr 320px; gap:var(--space-6); align-items:start; }

/* DASHBOARD LAYOUT */
.layout-dashboard { display:grid; grid-template-columns:240px 1fr; min-height:100vh; }

/* DASHBOARD SHELL */
.dashboard-shell {
  display:grid;
  grid-template-columns:240px 1fr;
  grid-template-rows:64px 1fr;
  grid-template-areas:"sidebar topbar" "sidebar content";
  min-height:100vh;
}
.dashboard-sidebar { grid-area:sidebar; }
.dashboard-topbar  { grid-area:topbar; }
.dashboard-content { grid-area:content; overflow-y:auto; padding:var(--space-6); background:var(--color-surface-subtle); }

/* AUTH LAYOUT */
.layout-auth { min-height:100vh; display:flex; align-items:center; justify-content:center; padding:var(--space-6); background:var(--gradient-body); }

/* SECTION */
.section        { padding:60px 0; }
.section-header { text-align:center; margin-bottom:var(--space-8); }
.content-offset { padding-top:72px; }

@media (max-width:992px) {
  .layout-tool      { grid-template-columns:1fr; }
  .layout-dashboard { grid-template-columns:1fr; }
  .dashboard-shell  { grid-template-columns:1fr; grid-template-areas:"topbar" "content"; }
  .dashboard-sidebar { display:none; }
  .bento-span-4, .bento-span-6, .bento-span-8 { grid-column:span 12; }
}
@media (max-width:768px) {
  .grid-cards { grid-template-columns:1fr; }
}
```

---

# PART 7 — COMPONENT BLUEPRINT

## Buttons

```css
.btn { display:inline-flex; align-items:center; justify-content:center; gap:var(--space-2); font-family:inherit; font-size:1rem; font-weight:600; line-height:1; white-space:nowrap; cursor:pointer; border:2px solid transparent; border-radius:var(--radius-pill); padding:10px 24px; height:44px; transition:all 0.25s ease; text-decoration:none; outline:none; }
.btn:focus-visible { box-shadow:0 0 0 3px var(--color-primary-ring); }
.btn:disabled { opacity:0.45; cursor:not-allowed; pointer-events:none; }
.btn-primary   { background:var(--color-primary); color:#fff; border-color:var(--color-primary); }
.btn-primary:hover  { background:var(--color-primary-dark); transform:scale(1.03); }
.btn-primary:active { transform:scale(0.98); }
.btn-ghost     { background:#f0f0f0; color:var(--color-primary); border-color:var(--color-primary); }
.btn-ghost:hover { background:var(--color-primary); color:#fff; border-color:var(--color-primary-dark); }
.btn-secondary { background:var(--color-secondary); color:#fff; border-color:var(--color-secondary); }
.btn-secondary:hover { background:var(--color-secondary-dark); transform:scale(1.03); }
.btn-dark      { background:#000; color:#fff; border-color:#000; border-radius:6px; }
.btn-dark:hover { background:#333; }
.btn-sm   { height:32px; padding:6px 16px; font-size:0.875rem; }
.btn-lg   { height:52px; padding:14px 32px; font-size:1.125rem; }
.btn-full { width:100%; }
```

## Cards

```css
.card { background:var(--color-surface-card); border:none; border-radius:var(--radius-xl); overflow:hidden; box-shadow:var(--shadow-md); transition:transform 0.3s ease, box-shadow 0.3s ease; }
.card-interactive:hover  { transform:translateY(-8px); box-shadow:var(--shadow-xl); }
.card-interactive:active { transform:translateY(-4px); box-shadow:var(--shadow-lg); }
.card-subtle   { background:linear-gradient(145deg,#fff,#f5f5f5); }
.card-bordered { border:1px solid var(--color-border-default); box-shadow:none; }
.card-bordered:hover { box-shadow:var(--shadow-md); }
.card-dark     { background:var(--color-dark-surface); border:1px solid var(--color-dark-border); color:var(--color-dark-text); }
.card-hero     { background:var(--gradient-hero-blue); color:#fff; border-radius:12px; padding:var(--space-10) var(--space-6); text-align:center; box-shadow:var(--shadow-xl); }
.card-body     { padding:var(--space-6); }
```

## Inputs & Forms

```css
.input { display:block; width:100%; height:44px; padding:10px 14px; font-family:inherit; font-size:0.9375rem; color:var(--color-text-primary); background:var(--color-surface-input); border:1.5px solid var(--color-border-default); border-radius:8px; outline:none; transition:border-color 0.2s ease, box-shadow 0.2s ease; }
.input::placeholder { color:var(--color-text-muted); }
.input:focus   { border-color:var(--color-border-focus); box-shadow:0 0 0 3px var(--color-primary-ring); }
.input-error   { border-color:var(--color-error); }
.input-error:focus { box-shadow:0 0 0 3px var(--color-error-alpha); }
.input-success { border-color:var(--color-success); }
.input:disabled { background:var(--color-surface-subtle); opacity:0.7; cursor:not-allowed; }
.form-label    { display:block; font-size:0.875rem; font-weight:500; color:var(--color-text-label); margin-bottom:var(--space-2); }
.form-helper   { font-size:0.8125rem; color:var(--color-text-muted); margin-top:var(--space-1); }
.form-helper-error { color:var(--color-error); }
.form-group    { margin-bottom:var(--space-5); }
.textarea      { height:auto; min-height:100px; resize:vertical; padding:12px 14px; line-height:1.6; }
```

## Navigation

```css
.navbar { position:fixed; top:0; left:0; right:0; z-index:1000; height:64px; background:var(--color-overlay-dark); box-shadow:var(--shadow-navbar); display:flex; align-items:center; }
.navbar-inner { max-width:1200px; margin:0 auto; padding:0 var(--space-5); width:100%; display:flex; align-items:center; justify-content:space-between; }
.navbar-brand { display:flex; align-items:center; gap:var(--space-2); color:#fff; font-weight:700; font-size:1.125rem; text-decoration:none; }
.nav-links { display:flex; align-items:center; gap:var(--space-1); list-style:none; margin:0; padding:0; }
.nav-link { color:rgba(255,255,255,0.85); font-size:0.9375rem; font-weight:500; padding:6px 12px; border-radius:6px; text-decoration:none; transition:all 0.2s ease; }
.nav-link:hover  { color:#fff; background:rgba(255,255,255,0.1); }
.nav-link.active { color:#fff; background:rgba(255,255,255,0.15); }
.sidebar-nav-item { display:flex; align-items:center; gap:var(--space-3); padding:9px var(--space-5); margin:1px var(--space-3); border-radius:8px; color:var(--color-text-secondary); font-size:0.9rem; font-weight:500; text-decoration:none; transition:all 0.15s ease; border-left:3px solid transparent; }
.sidebar-nav-item:hover  { background:var(--color-surface-hover); color:var(--color-text-primary); }
.sidebar-nav-item.active { background:var(--color-primary-light); color:var(--color-primary); border-left-color:var(--color-primary); font-weight:600; }
```

## Badges, Alerts, Toasts, Loading

```css
.badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; letter-spacing:0.03em; text-transform:uppercase; }
.badge-success { background:var(--color-success-light); color:var(--color-success-dark); }
.badge-warning { background:var(--color-warning-light); color:var(--color-warning-dark); }
.badge-error   { background:var(--color-error-light);   color:var(--color-error-dark); }
.badge-info    { background:var(--color-info-light);    color:var(--color-primary-dark); }

.alert { display:flex; align-items:flex-start; gap:var(--space-3); padding:var(--space-4) var(--space-5); border-radius:10px; font-size:0.9375rem; border-left:4px solid; }
.alert-success { background:var(--color-success-light); border-color:var(--color-success); color:var(--color-success-dark); }
.alert-error   { background:var(--color-error-light);   border-color:var(--color-error);   color:var(--color-error-dark); }
.alert-warning { background:var(--color-warning-light); border-color:var(--color-warning); color:var(--color-warning-dark); }

.toast { position:fixed; bottom:24px; right:24px; z-index:9999; min-width:280px; max-width:400px; padding:var(--space-4) var(--space-5); background:#1a1a2e; color:#fff; border-radius:10px; box-shadow:var(--shadow-xl); font-size:0.9375rem; display:flex; align-items:center; gap:var(--space-3); animation:toast-in 0.3s ease forwards; }
@keyframes toast-in { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }

.spinner { width:24px; height:24px; border:3px solid var(--color-border-subtle); border-top-color:var(--color-primary); border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

.skeleton { background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%); background-size:200% 100%; animation:shimmer 1.5s infinite; border-radius:6px; }
@keyframes shimmer { 0% { background-position:200% 0; } 100% { background-position:-200% 0; } }
.skeleton-text  { height:16px; margin-bottom:8px; }
.skeleton-title { height:24px; width:60%; margin-bottom:16px; }
.skeleton-card  { height:120px; border-radius:14px; }
```

## Shadow & Radius Scale

```css
:root {
  --shadow-xs:     0 1px 2px rgba(0,0,0,0.06);
  --shadow-sm:     0 2px 4px rgba(0,0,0,0.08);
  --shadow-md:     0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg:     0 8px 24px rgba(0,0,0,0.12);
  --shadow-xl:     0 16px 40px rgba(0,0,0,0.15);
  --shadow-2xl:    0 24px 64px rgba(0,0,0,0.20);
  --shadow-navbar: 0 2px 4px rgba(0,0,0,0.10);
  --shadow-notion: rgba(15,15,15,0.05) 0px 0px 0px 1px, rgba(15,15,15,0.10) 0px 3px 6px, rgba(15,15,15,0.20) 0px 9px 24px;
  --ring-primary:  0 0 0 3px rgba(0,123,255,0.40);
  --ring-error:    0 0 0 3px rgba(231,76,60,0.30);
  --ring-success:  0 0 0 3px rgba(76,175,80,0.30);
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-pill: 999px;
  --radius-full: 50%;
}
```

---

# PART 8 — PREMIUM EFFECTS SYSTEM

## Glassmorphism

Frosted-glass effect. Use on top of colorful/gradient backgrounds — never on plain white.

```css
.glass-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}
.glass-apple {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.glass-dark {
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
}
.glass-navbar {
  background: rgba(255, 255, 255, 0.80);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.20);
}
```

**Rules:** Background opacity 10–25% subtle / 60–80% strong. Blur 12–24px. Always add white border + shadow. Requires colorful background behind it.

---

## Neumorphism

Soft extruded plastic look. Light gray backgrounds only (`#e0e5ec`). Never on white or dark.

```css
.neu-surface {
  background: #e0e5ec;
  border-radius: 16px;
  box-shadow: 6px 6px 12px #b8bec7, -6px -6px 12px #ffffff;
}
.neu-button {
  background: #e0e5ec;
  border: none; border-radius: 12px; padding: 12px 24px;
  box-shadow: 5px 5px 10px #b8bec7, -5px -5px 10px #ffffff;
  cursor: pointer; transition: box-shadow 0.2s ease;
}
.neu-button:active {
  box-shadow: inset 4px 4px 8px #b8bec7, inset -4px -4px 8px #ffffff;
}
.neu-input {
  background: #e0e5ec; border: none; border-radius: 10px; padding: 12px 16px;
  box-shadow: inset 4px 4px 8px #b8bec7, inset -4px -4px 8px #ffffff;
  outline: none;
}
```

---

## Soft UI (Modern SaaS Cards)

Production-safe middle ground between flat and neumorphism.

```css
.soft-card {
  background: #ffffff; border-radius: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 16px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.06);
}
.soft-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 16px 32px rgba(0,0,0,0.10);
  transform: translateY(-4px);
}
.soft-input {
  background: #f8f9fa; border: 1.5px solid #e9ecef; border-radius: 10px;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.04);
}
.soft-input:focus { background: #ffffff; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-ring); }
```

---

## AI Product Design

```css
.chat-bubble-user { background:var(--color-primary); color:#fff; border-radius:18px 18px 4px 18px; padding:12px 16px; max-width:75%; align-self:flex-end; font-size:0.9375rem; line-height:1.5; }
.chat-bubble-ai   { background:var(--color-surface-subtle); color:var(--color-text-primary); border-radius:18px 18px 18px 4px; padding:12px 16px; max-width:85%; align-self:flex-start; font-size:0.9375rem; line-height:1.6; border:1px solid var(--color-border-subtle); }

.typing-indicator { display:flex; gap:4px; padding:12px 16px; background:var(--color-surface-subtle); border-radius:18px 18px 18px 4px; width:fit-content; }
.typing-dot { width:8px; height:8px; background:var(--color-text-muted); border-radius:50%; animation:typing-bounce 1.2s infinite; }
.typing-dot:nth-child(2) { animation-delay:0.2s; }
.typing-dot:nth-child(3) { animation-delay:0.4s; }
@keyframes typing-bounce { 0%,60%,100% { transform:translateY(0); } 30% { transform:translateY(-6px); } }

.text-ai-gradient { background:linear-gradient(135deg,#667eea,#764ba2,#f093fb); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.ai-glow { box-shadow:0 0 20px rgba(102,126,234,0.3), 0 0 60px rgba(102,126,234,0.1); }
.streaming-cursor::after { content:'▋'; animation:blink 0.7s infinite; color:var(--color-primary); }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
```

---

## Enterprise Design

```css
.enterprise-card { background:#ffffff; border:1px solid #d1d5db; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.06); }
.enterprise-table { width:100%; border-collapse:collapse; font-size:0.875rem; }
.enterprise-table th { background:#f9fafb; border-bottom:2px solid #e5e7eb; padding:10px 16px; text-align:left; font-weight:600; color:#374151; font-size:0.8125rem; text-transform:uppercase; letter-spacing:0.05em; }
.enterprise-table td { padding:10px 16px; border-bottom:1px solid #f3f4f6; color:#374151; vertical-align:middle; }
.enterprise-table tr:hover td { background:#f9fafb; }
.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
.status-dot-active  { background:var(--color-success); }
.status-dot-warning { background:var(--color-warning); }
.status-dot-error   { background:var(--color-error); }
```

---

## Luxury Design

```css
.luxury-card { background:#0a0a0a; border:1px solid rgba(212,175,55,0.3); border-radius:2px; padding:40px; color:#f5f5f0; }
.luxury-btn { background:transparent; color:#d4af37; border:1px solid #d4af37; border-radius:0; padding:14px 40px; font-size:0.8125rem; letter-spacing:0.15em; text-transform:uppercase; transition:all 0.4s ease; }
.luxury-btn:hover { background:#d4af37; color:#0a0a0a; }
.luxury-divider { border:none; height:1px; background:linear-gradient(to right,transparent,rgba(212,175,55,0.5),transparent); margin:40px 0; }
```

---

# PART 9 — ANIMATION SYSTEM

```css
:root {
  --duration-instant:100ms; --duration-fast:150ms; --duration-normal:250ms;
  --duration-medium:350ms;  --duration-slow:450ms; --duration-crawl:600ms;
  --ease-out:    cubic-bezier(0, 0, 0.2, 1);
  --ease-in:     cubic-bezier(0.4, 0, 1, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fade-in    { from{opacity:0} to{opacity:1} }
@keyframes slide-up   { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
@keyframes scale-in   { from{opacity:0;transform:scale(0.95)} to{opacity:1;transform:scale(1)} }
@keyframes slide-right{ from{opacity:0;transform:translateX(-24px)} to{opacity:1;transform:translateX(0)} }

.animate-fade-in   { animation:fade-in   var(--duration-slow)   var(--ease-out) both; }
.animate-slide-up  { animation:slide-up  var(--duration-slow)   var(--ease-out) both; }
.animate-scale-in  { animation:scale-in  var(--duration-medium) var(--ease-out) both; }
.animate-slide-right { animation:slide-right var(--duration-medium) var(--ease-out) both; }

.stagger-1{animation-delay:50ms}  .stagger-2{animation-delay:100ms}
.stagger-3{animation-delay:150ms} .stagger-4{animation-delay:200ms}
.stagger-5{animation-delay:250ms} .stagger-6{animation-delay:300ms}

.scroll-reveal { opacity:0; transform:translateY(24px); transition:opacity var(--duration-crawl) var(--ease-out), transform var(--duration-crawl) var(--ease-out); }
.scroll-reveal.visible { opacity:1; transform:translateY(0); }

.hover-lift { transition:transform var(--duration-normal) var(--ease-out), box-shadow var(--duration-normal) var(--ease-out); }
.hover-lift:hover { transform:translateY(-8px); box-shadow:var(--shadow-xl); }
.hover-scale { transition:transform var(--duration-normal) var(--ease-out); }
.hover-scale:hover  { transform:scale(1.03); }
.hover-scale:active { transform:scale(0.97); }

@media (prefers-reduced-motion:reduce) {
  *,*::before,*::after { animation-duration:0.01ms !important; animation-iteration-count:1 !important; transition-duration:0.01ms !important; }
}
```

```javascript
// Scroll reveal setup
const revealObserver = new IntersectionObserver(
  (entries) => entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); }
  }),
  { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
);
document.querySelectorAll('.scroll-reveal').forEach((el) => revealObserver.observe(el));
```

| Context | Duration | Easing | Transform |
|---|---|---|---|
| Button hover | 200–250ms | ease | scale(1.03) |
| Button press | 100ms | ease-in | scale(0.97) |
| Card hover lift | 250–300ms | ease | translateY(-8px) |
| Dropdown open | 200ms | ease-out | translateY(-8px)→0 + opacity |
| Modal entrance | 300ms | ease-out | scale(0.95)→1 + opacity |
| Toast entrance | 300ms | ease-out | translateY(16px)→0 |
| Scroll reveal | 500ms | ease-out | translateY(24px)→0 |
| Spinner | 700ms | linear | rotate(360deg) |

---

# PART 10 — AUTHENTICATION DESIGN

## Layout

```css
.auth-page { min-height:100vh; display:grid; grid-template-columns:1fr 1fr; }
.auth-brand-panel { background:var(--gradient-hero-blue); display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px; color:#fff; }
.auth-form-panel  { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px 80px; background:#fff; }
.auth-card { width:100%; max-width:420px; background:#fff; border-radius:16px; padding:40px; box-shadow:var(--shadow-xl); }
@media (max-width:768px) { .auth-page{grid-template-columns:1fr} .auth-brand-panel{display:none} .auth-form-panel{padding:40px 24px} }
```

## Login Page Rules

- Heading: "Welcome back" — never "Login"
- Email field first, password field second
- "Show password" toggle on password field
- "Forgot password?" link right-aligned beside password label
- "Remember me" checkbox left-aligned
- CTA: full-width "Sign in"
- Social login (Google first) above form with "or" divider
- Register link at the very bottom

## Register Page Rules

- Heading: "Create your account"
- Fields: Full name → Email → Password → Confirm password
- Password strength indicator below password field
- Terms of service checkbox before submit
- CTA: "Create account" — never "Register" or "Submit"

```css
.password-strength { display:flex; gap:4px; margin-top:8px; }
.strength-bar { height:4px; flex:1; border-radius:2px; background:var(--color-border-subtle); transition:background 0.3s ease; }
.strength-bar.weak   { background:var(--color-error); }
.strength-bar.medium { background:var(--color-warning); }
.strength-bar.strong { background:var(--color-success); }
```

## OTP Verification

```css
.otp-group { display:flex; gap:12px; justify-content:center; margin:32px 0; }
.otp-input { width:52px; height:60px; text-align:center; font-size:1.5rem; font-weight:700; border:2px solid var(--color-border-default); border-radius:10px; outline:none; transition:border-color 0.2s ease, box-shadow 0.2s ease; }
.otp-input:focus  { border-color:var(--color-primary); box-shadow:0 0 0 3px var(--color-primary-ring); }
.otp-input.filled { border-color:var(--color-success); background:var(--color-success-light); }
```

```javascript
document.querySelectorAll('.otp-input').forEach((input, index, inputs) => {
  input.addEventListener('input', (e) => {
    if (e.target.value.length === 1 && index < inputs.length - 1) inputs[index + 1].focus();
    if (index === inputs.length - 1 && e.target.value) document.getElementById('otp-form').submit();
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Backspace' && !e.target.value && index > 0) inputs[index - 1].focus();
  });
});
```

## Auth Rules Summary

| Rule | Value |
|---|---|
| Auth card max-width | 420px |
| Auth card padding | 40px |
| Logo height | 40–48px |
| Input height | 44px |
| CTA button | Full-width, primary |
| Social login | Above form divider |
| Error messages | Inline below field, red text |
| Background | Warm gradient or split panel |

---

# PART 11 — DASHBOARD ARCHITECTURE

## Sidebar

```css
.sidebar { background:#fff; border-right:1px solid var(--color-border-subtle); display:flex; flex-direction:column; padding:var(--space-4) 0; position:sticky; top:0; height:100vh; overflow-y:auto; }
.sidebar-logo { padding:var(--space-4) var(--space-5); margin-bottom:var(--space-4); border-bottom:1px solid var(--color-border-subtle); }
.sidebar-section-label { font-size:0.6875rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--color-text-muted); padding:var(--space-4) var(--space-5) var(--space-2); }
.sidebar-footer { margin-top:auto; padding:var(--space-4) var(--space-5); border-top:1px solid var(--color-border-subtle); }
```

## Topbar

```css
.topbar { background:#fff; border-bottom:1px solid var(--color-border-subtle); display:flex; align-items:center; justify-content:space-between; padding:0 var(--space-6); height:64px; position:sticky; top:0; z-index:100; }
.topbar-search { display:flex; align-items:center; gap:var(--space-2); background:var(--color-surface-subtle); border:1px solid var(--color-border-default); border-radius:8px; padding:7px 12px; width:280px; cursor:pointer; transition:all 0.2s ease; }
.topbar-search:hover { border-color:var(--color-border-strong); }
.topbar-search-kbd { font-size:0.75rem; color:var(--color-text-muted); background:var(--color-surface-card); border:1px solid var(--color-border-default); border-radius:4px; padding:2px 6px; margin-left:auto; }
.topbar-icon-btn { width:36px; height:36px; display:flex; align-items:center; justify-content:center; border-radius:8px; border:none; background:transparent; color:var(--color-text-secondary); cursor:pointer; transition:all 0.15s ease; position:relative; }
.topbar-icon-btn:hover { background:var(--color-surface-hover); color:var(--color-text-primary); }
.notification-badge { position:absolute; top:4px; right:4px; width:8px; height:8px; background:var(--color-error); border-radius:50%; border:2px solid #fff; }
.avatar { width:36px; height:36px; border-radius:50%; background:var(--color-primary); color:#fff; display:flex; align-items:center; justify-content:center; font-size:0.875rem; font-weight:600; cursor:pointer; flex-shrink:0; }
```

## KPI Cards

```css
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:var(--space-5); margin-bottom:var(--space-7); }
.kpi-card { background:#fff; border:1px solid var(--color-border-subtle); border-radius:12px; padding:var(--space-5) var(--space-6); display:flex; flex-direction:column; gap:var(--space-3); }
.kpi-label { font-size:0.8125rem; font-weight:500; color:var(--color-text-secondary); text-transform:uppercase; letter-spacing:0.05em; }
.kpi-value { font-size:2rem; font-weight:700; color:var(--color-text-primary); line-height:1.1; letter-spacing:-0.02em; }
.kpi-change { display:flex; align-items:center; gap:4px; font-size:0.8125rem; font-weight:500; }
.kpi-change-up   { color:var(--color-success); }
.kpi-change-down { color:var(--color-error); }
.kpi-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.25rem; background:var(--color-primary-light); color:var(--color-primary); margin-left:auto; }
```

## Data Tables

```css
.data-table-wrapper { background:#fff; border:1px solid var(--color-border-subtle); border-radius:12px; overflow:hidden; }
.data-table-header  { display:flex; align-items:center; justify-content:space-between; padding:var(--space-5) var(--space-6); border-bottom:1px solid var(--color-border-subtle); }
.data-table { width:100%; border-collapse:collapse; font-size:0.875rem; }
.data-table th { background:var(--color-surface-subtle); padding:10px 16px; text-align:left; font-weight:600; font-size:0.8125rem; color:var(--color-text-secondary); text-transform:uppercase; letter-spacing:0.04em; border-bottom:1px solid var(--color-border-subtle); white-space:nowrap; }
.data-table td { padding:12px 16px; border-bottom:1px solid var(--color-border-subtle); color:var(--color-text-primary); vertical-align:middle; }
.data-table tr:last-child td { border-bottom:none; }
.data-table tr:hover td { background:var(--color-surface-subtle); }
.data-table-pagination { display:flex; align-items:center; justify-content:space-between; padding:var(--space-4) var(--space-6); border-top:1px solid var(--color-border-subtle); font-size:0.875rem; color:var(--color-text-secondary); }
```

## Settings Page

```css
.settings-layout { display:grid; grid-template-columns:220px 1fr; gap:var(--space-8); max-width:960px; }
.settings-nav-item { display:block; padding:8px 12px; border-radius:6px; font-size:0.9rem; font-weight:500; color:var(--color-text-secondary); text-decoration:none; transition:all 0.15s ease; margin-bottom:2px; }
.settings-nav-item:hover  { background:var(--color-surface-hover); color:var(--color-text-primary); }
.settings-nav-item.active { background:var(--color-primary-light); color:var(--color-primary); font-weight:600; }
.settings-section { background:#fff; border:1px solid var(--color-border-subtle); border-radius:12px; overflow:hidden; margin-bottom:var(--space-6); }
.settings-section-header { padding:var(--space-5) var(--space-6); border-bottom:1px solid var(--color-border-subtle); }
.settings-section-body { padding:var(--space-6); }
.settings-row { display:flex; align-items:center; justify-content:space-between; padding:var(--space-4) 0; border-bottom:1px solid var(--color-border-subtle); }
.settings-row:last-child { border-bottom:none; }
```

## Profile & Notifications

```css
.profile-card { display:flex; align-items:center; gap:var(--space-5); padding:var(--space-6); background:#fff; border:1px solid var(--color-border-subtle); border-radius:12px; margin-bottom:var(--space-6); }
.profile-avatar-lg { width:72px; height:72px; border-radius:50%; background:var(--color-primary); color:#fff; display:flex; align-items:center; justify-content:center; font-size:1.5rem; font-weight:700; flex-shrink:0; }
.notification-item { display:flex; gap:var(--space-4); padding:var(--space-4) var(--space-5); border-bottom:1px solid var(--color-border-subtle); transition:background 0.15s ease; cursor:pointer; }
.notification-item:hover  { background:var(--color-surface-subtle); }
.notification-item.unread { background:var(--color-primary-light); }
.notification-dot { width:8px; height:8px; border-radius:50%; background:var(--color-primary); flex-shrink:0; margin-top:6px; }
```

---

# PART 12 — AI SAAS & MODERN 2026 DESIGN TRENDS

## Bento Grid

```css
.bento-grid { display:grid; grid-template-columns:repeat(12,1fr); grid-auto-rows:160px; gap:var(--space-4); }
.bento-1x1 { grid-column:span 3; grid-row:span 1; }
.bento-2x1 { grid-column:span 6; grid-row:span 1; }
.bento-2x2 { grid-column:span 6; grid-row:span 2; }
.bento-4x1 { grid-column:span 12; grid-row:span 1; }
.bento-cell { background:#fff; border:1px solid var(--color-border-subtle); border-radius:16px; padding:var(--space-6); overflow:hidden; transition:transform 0.3s ease, box-shadow 0.3s ease; }
.bento-cell:hover { transform:scale(1.01); box-shadow:var(--shadow-lg); }
.bento-primary { background:var(--color-primary); color:#fff; border-color:transparent; }
.bento-dark    { background:#0F0F0F; color:#fff; border-color:transparent; }
@media (max-width:768px) { .bento-1x1,.bento-2x1,.bento-2x2,.bento-4x1 { grid-column:span 12; grid-row:span 1; } }
```

## Floating Cards

```css
.floating-card {
  background:#fff; border-radius:20px; padding:var(--space-7);
  box-shadow: 0 1px 1px rgba(0,0,0,0.04), 0 2px 2px rgba(0,0,0,0.04),
              0 4px 4px rgba(0,0,0,0.04), 0 8px 8px rgba(0,0,0,0.04),
              0 16px 16px rgba(0,0,0,0.04);
  transform:translateY(-4px); transition:transform 0.4s ease, box-shadow 0.4s ease;
}
.floating-card:hover {
  transform:translateY(-12px);
  box-shadow: 0 4px 4px rgba(0,0,0,0.04), 0 8px 8px rgba(0,0,0,0.04),
              0 16px 16px rgba(0,0,0,0.04), 0 32px 32px rgba(0,0,0,0.04);
}
```

## Gradient Mesh Background

```css
.gradient-mesh {
  background-color:#ffffff;
  background-image:
    radial-gradient(at 40% 20%, hsl(228,100%,74%) 0px, transparent 50%),
    radial-gradient(at 80% 0%,  hsl(189,100%,56%) 0px, transparent 50%),
    radial-gradient(at 0%  50%, hsl(355,100%,93%) 0px, transparent 50%),
    radial-gradient(at 80% 50%, hsl(340,100%,76%) 0px, transparent 50%),
    radial-gradient(at 0%  100%,hsl(22, 100%,77%) 0px, transparent 50%);
}
.gradient-mesh-animated {
  background:linear-gradient(-45deg,#ee7752,#e73c7e,#23a6d5,#23d5ab);
  background-size:400% 400%;
  animation:gradient-shift 12s ease infinite;
}
@keyframes gradient-shift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
```

## Micro Interactions

```css
.like-btn:active { transform:scale(0.85); }
.like-btn.liked  { animation:like-burst 0.4s var(--ease-spring) forwards; }
@keyframes like-burst { 0%{transform:scale(1)} 40%{transform:scale(1.3)} 70%{transform:scale(0.9)} 100%{transform:scale(1)} }

.toggle { width:44px; height:24px; background:var(--color-border-default); border-radius:999px; position:relative; cursor:pointer; transition:background 0.2s ease; }
.toggle.on { background:var(--color-success); }
.toggle-thumb { width:18px; height:18px; background:#fff; border-radius:50%; position:absolute; top:3px; left:3px; transition:transform 0.2s var(--ease-spring); box-shadow:0 1px 3px rgba(0,0,0,0.2); }
.toggle.on .toggle-thumb { transform:translateX(20px); }
```

## Command Palette

```css
.cmd-overlay { position:fixed; inset:0; z-index:9999; background:rgba(0,0,0,0.5); backdrop-filter:blur(4px); display:flex; align-items:flex-start; justify-content:center; padding-top:15vh; animation:fade-in 0.15s ease; }
.cmd-panel { width:100%; max-width:560px; background:#fff; border-radius:16px; box-shadow:var(--shadow-2xl); overflow:hidden; animation:scale-in 0.15s var(--ease-out); }
.cmd-input { width:100%; padding:16px 20px; font-size:1rem; border:none; outline:none; border-bottom:1px solid var(--color-border-subtle); background:transparent; }
.cmd-results { max-height:360px; overflow-y:auto; padding:var(--space-2) 0; }
.cmd-item { display:flex; align-items:center; gap:var(--space-3); padding:10px 16px; cursor:pointer; transition:background 0.1s ease; font-size:0.9375rem; }
.cmd-item:hover,.cmd-item.selected { background:var(--color-primary-light); color:var(--color-primary); }
.cmd-item-kbd { margin-left:auto; font-size:0.75rem; color:var(--color-text-muted); background:var(--color-surface-subtle); border:1px solid var(--color-border-default); border-radius:4px; padding:2px 6px; }
.cmd-section-label { font-size:0.75rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; color:var(--color-text-muted); padding:8px 16px 4px; }
```

## Glass Sidebar

```css
.glass-sidebar { width:240px; height:100vh; background:rgba(255,255,255,0.80); backdrop-filter:blur(20px) saturate(180%); -webkit-backdrop-filter:blur(20px) saturate(180%); border-right:1px solid rgba(255,255,255,0.30); box-shadow:4px 0 24px rgba(0,0,0,0.06); position:sticky; top:0; }
```

## AI Chat Interface

```css
.ai-chat-container { display:flex; flex-direction:column; height:100%; max-width:760px; margin:0 auto; }
.ai-chat-messages  { flex:1; overflow-y:auto; padding:var(--space-6); display:flex; flex-direction:column; gap:var(--space-5); }
.chat-message { display:flex; gap:var(--space-4); align-items:flex-start; }
.chat-message.user { flex-direction:row-reverse; }
.chat-avatar { width:32px; height:32px; border-radius:50%; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:0.875rem; font-weight:600; }
.chat-avatar-ai   { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; }
.chat-avatar-user { background:var(--color-primary); color:#fff; }
.chat-bubble { max-width:75%; padding:12px 16px; border-radius:16px; font-size:0.9375rem; line-height:1.6; }
.chat-bubble-ai   { background:var(--color-surface-subtle); border:1px solid var(--color-border-subtle); border-radius:4px 16px 16px 16px; }
.chat-bubble-user { background:var(--color-primary); color:#fff; border-radius:16px 4px 16px 16px; }
.ai-chat-input-area { padding:var(--space-4) var(--space-6); border-top:1px solid var(--color-border-subtle); background:#fff; }
.ai-chat-input-wrapper { display:flex; align-items:flex-end; gap:var(--space-3); background:var(--color-surface-subtle); border:1.5px solid var(--color-border-default); border-radius:14px; padding:10px 14px; transition:border-color 0.2s ease, box-shadow 0.2s ease; }
.ai-chat-input-wrapper:focus-within { border-color:var(--color-border-focus); box-shadow:0 0 0 3px var(--color-primary-ring); }
.ai-chat-textarea { flex:1; border:none; outline:none; background:transparent; font-family:inherit; font-size:0.9375rem; line-height:1.5; resize:none; max-height:200px; }
.ai-send-btn { width:36px; height:36px; border-radius:8px; background:var(--color-primary); color:#fff; border:none; cursor:pointer; flex-shrink:0; display:flex; align-items:center; justify-content:center; transition:background 0.2s ease; }
.ai-send-btn:hover    { background:var(--color-primary-dark); }
.ai-send-btn:disabled { background:var(--color-border-default); cursor:not-allowed; }
```

---

# PART 13 — MOBILE-FIRST RULES

```css
body { overflow-x:hidden; }
img  { max-width:100%; height:auto; }
*, *::before, *::after { box-sizing:border-box; }

@media (max-width:768px) {
  .text-display         { font-size:2rem; }
  .text-section-heading { font-size:1.5rem; }
  .text-card-heading    { font-size:1.125rem; }
  .text-kpi-value       { font-size:1.5rem; }
}
@media (max-width:576px) {
  .container-narrow,.container-default,.container-wide { padding:0 16px; }
  .btn-mobile-full { width:100%; }
  .grid-cards,.layout-thirds,.layout-form-preview,.settings-layout { grid-template-columns:1fr; }
}

.touch-target { min-height:44px; min-width:44px; display:flex; align-items:center; justify-content:center; }

.mobile-bottom-nav { display:none; position:fixed; bottom:0; left:0; right:0; background:#fff; border-top:1px solid var(--color-border-subtle); padding:8px 0 env(safe-area-inset-bottom); z-index:1000; }
@media (max-width:768px) { .mobile-bottom-nav{display:flex} .dashboard-sidebar{display:none} }
.mobile-nav-item { flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; padding:8px; color:var(--color-text-muted); font-size:0.6875rem; font-weight:500; text-decoration:none; transition:color 0.15s ease; }
.mobile-nav-item.active { color:var(--color-primary); }
.safe-top    { padding-top:env(safe-area-inset-top); }
.safe-bottom { padding-bottom:env(safe-area-inset-bottom); }
```

| Rule | Value |
|---|---|
| Design viewport | 375px |
| Horizontal padding | 16–20px minimum |
| Touch target | 44×44px minimum |
| Hero font | 2rem on mobile |
| Section font | 1.5rem on mobile |
| Buttons | Full-width on mobile |
| Columns | Always stack to 1 column |
| Navigation | Bottom nav bar on mobile |
| Sidebar | Hidden on mobile |

---

# PART 14 — ACCESSIBILITY SYSTEM

```html
<!-- LIVE REGION -->
<div aria-live="polite" aria-atomic="true" id="status-region"></div>

<!-- MODAL -->
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Dialog Title</h2>
</div>

<!-- LOADING BUTTON -->
<button aria-busy="true" aria-label="Loading, please wait">
  <span class="spinner" aria-hidden="true"></span> Loading...
</button>

<!-- ERROR INPUT -->
<input id="email" aria-describedby="email-error" aria-invalid="true">
<span id="email-error" role="alert" class="form-helper-error">Please enter a valid email.</span>

<!-- SKIP LINK -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

```css
.skip-link { position:absolute; top:-100%; left:16px; background:var(--color-primary); color:#fff; padding:8px 16px; border-radius:0 0 8px 8px; font-weight:600; z-index:9999; transition:top 0.2s ease; }
.skip-link:focus { top:0; }
:focus-visible { outline:3px solid var(--color-primary); outline-offset:2px; }
:focus:not(:focus-visible) { outline:none; }
```

**Accessibility Checklist:**
```
STRUCTURE
[ ] One <h1> per page
[ ] Sequential heading levels (h1→h2→h3)
[ ] <nav>, <main>, <footer>, <aside> landmarks
[ ] Skip navigation link

INTERACTIVE
[ ] All buttons: <button> element
[ ] Focus order = visual reading order
[ ] Visible focus styles on all interactive elements
[ ] Touch targets: 44×44px minimum

FORMS
[ ] Every input has a <label> with for/id
[ ] No placeholder-only labels
[ ] Errors: aria-describedby + role="alert"
[ ] Required fields marked (not just color)

IMAGES
[ ] All <img> have alt text
[ ] Decorative images: alt=""
[ ] Icon buttons: aria-label

DYNAMIC CONTENT
[ ] Loading: aria-live="polite"
[ ] Errors: aria-live="assertive"
[ ] Modals: focus trap + restore on close

COLOR & CONTRAST
[ ] Normal text: 4.5:1 minimum
[ ] Large text: 3:1 minimum
[ ] Color never the only differentiator

MOTION
[ ] prefers-reduced-motion respected
[ ] No content flashes 3+ times/second
```

---

# PART 15 — PERFORMANCE DESIGN RULES

1. **Animate only `transform` and `opacity`.** These trigger GPU compositing. `width`, `height`, `top`, `left` cause layout reflow every frame.
2. **Use `will-change` sparingly.** Only on elements that will definitely animate. Overuse wastes GPU memory.
3. **Lazy-load images below the fold.** `<img loading="lazy">` on every non-hero image.
4. **Use `font-display: swap`.** Prevents invisible text during font load.
5. **Skeleton screens over spinners for content.** Users perceive skeletons as faster because they see layout structure.
6. **Debounce search inputs at 300ms.** Never fire API calls on every keystroke.
7. **Use CSS variables for theme values.** Variable changes trigger repaint, not reflow.
8. **Avoid animating `box-shadow`.** Use `filter: drop-shadow()` instead — GPU-accelerated.
9. **Use `contain: layout` on isolated components.** Speeds up reflow calculations.
10. **Preload critical fonts:** `<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>`

---

# PART 16 — DESIGN PSYCHOLOGY

**Pill buttons increase CTR.** Rounded shapes are perceived as friendlier and more inviting. Sharp corners subconsciously signal "stop." Pill buttons signal "safe to proceed." Use pills for consumer SaaS, landing pages, mobile. Use rectangles for enterprise and developer tools.

**Large whitespace feels premium.** Luxury brands use extreme whitespace. Users associate whitespace with quality because it reduces cognitive load. Section padding under 60px feels budget. 80–96px feels premium.

**Gradients attract attention.** The eye moves from darker to lighter end of a gradient. Use gradients on the most important element. Never on everything — they lose their attention-directing power.

**Glassmorphism feels modern.** References real-world frosted glass — a material users associate with premium physical products (Apple devices). The blur creates depth. Only works on colorful backgrounds.

**Card elevation increases trust.** Shadows simulate physical depth. Physical objects feel more real and trustworthy than flat graphics. No shadow = cheap. Small shadow = professional. Large shadow = important.

**Left-to-right reading creates CTA placement rules.** Users scan in an F-pattern. Logo top-left. Nav top-right. Hero text left-aligned. CTA after the value proposition. Never put a CTA before the value proposition.

**Color temperature affects perceived speed.** Warm colors (red, orange) feel urgent. Cool colors (blue, green) feel trustworthy. Use warm accents for time-sensitive CTAs. Use cool primaries for trust-building CTAs.

**Typography weight signals authority.** `font-weight: 300` = casual. `400` = neutral. `500` = confident. `600` = authoritative. `700` = commanding. Use weight before size to establish hierarchy.

**Consistent spacing signals craftsmanship.** Consistent patterns are processed as intentional. Inconsistent patterns are processed as errors. The brain is a pattern-recognition machine.

**Loading states prevent abandonment.** Users abandon pages that don't respond within 3 seconds. A spinner doesn't make the page faster — it makes the wait feel shorter. Show a loading indicator within 100ms of any user action.

---

# PART 17 — DESIGN AUDIT CHECKLIST

Run before every deployment.

**Visual Audit**
```
[ ] Maximum 2 font families
[ ] Heading hierarchy is clear (H1 > H2 > H3)
[ ] Body text is 15–17px
[ ] Line height 1.5–1.7 for body, 1.1–1.3 for headings
[ ] No more than 5 font sizes on a single page
[ ] One primary color used consistently
[ ] Semantic colors used correctly
[ ] No more than 3 intentional colors
[ ] All spacing values are multiples of 4 or 8
[ ] Section padding is 60px minimum
[ ] Card padding is consistent across all cards
[ ] All buttons of the same type have the same height
[ ] All cards have the same border-radius
[ ] All cards have the same resting shadow
[ ] Hover states exist on all interactive elements
[ ] Focus states exist on all interactive elements
```

**Accessibility Audit**
```
[ ] All images have alt text
[ ] All form inputs have visible labels
[ ] Color is never the only differentiator
[ ] Contrast ratio: 4.5:1 for normal text
[ ] Contrast ratio: 3:1 for large text and UI components
[ ] All interactive elements are keyboard-navigable
[ ] Focus order follows visual reading order
[ ] Dynamic content has aria-live regions
[ ] Error messages are associated with inputs
[ ] Touch targets are 44×44px minimum
[ ] Skip navigation link exists
[ ] prefers-reduced-motion is respected
```

**Responsive Audit**
```
[ ] Tested at 375px (iPhone SE)
[ ] Tested at 768px (tablet)
[ ] Tested at 1280px (laptop)
[ ] Tested at 1920px (desktop)
[ ] No horizontal scroll at any breakpoint
[ ] All columns stack correctly on mobile
[ ] All buttons are full-width on mobile
[ ] Font sizes scale down at 768px
[ ] Images don't overflow their containers
[ ] Fixed navbar has correct content offset
```

**Performance Audit**
```
[ ] Only transform and opacity are animated
[ ] Images have loading="lazy" below the fold
[ ] Web fonts use font-display: swap
[ ] No layout-triggering properties animated
[ ] Search inputs are debounced
[ ] Loading states exist for all async operations
[ ] Critical fonts are preloaded
```

**Consistency Audit**
```
[ ] Same button styles used throughout
[ ] Same card styles used throughout
[ ] Same input styles used throughout
[ ] Same shadow values used throughout
[ ] Same border-radius values used throughout
[ ] Same transition durations used throughout
[ ] No inline styles that override the system
[ ] No magic numbers (unexplained pixel values)
```

---

# PART 18 — PAGE TEMPLATES

## Landing Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product — Tagline</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="design-system.css">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <nav class="navbar">
    <div class="navbar-inner">
      <a href="/" class="navbar-brand">
        <img src="logo.svg" alt="Logo" style="height:36px;">
        <span>ProductName</span>
      </a>
      <ul class="nav-links">
        <li><a href="#features" class="nav-link">Features</a></li>
        <li><a href="#pricing" class="nav-link">Pricing</a></li>
        <li><a href="/login" class="nav-link">Sign in</a></li>
        <li><a href="/signup" class="btn btn-ghost btn-sm">Get started</a></li>
      </ul>
    </div>
  </nav>

  <main id="main-content" class="content-offset">

    <!-- HERO -->
    <section style="padding:96px 0; text-align:center; background:var(--gradient-body);">
      <div class="container-hero">
        <div class="card-hero animate-scale-in">
          <h1 class="text-display">Your Value Proposition</h1>
          <p style="font-size:1.2rem; margin:24px auto; opacity:0.9; max-width:560px;">
            One sentence. Who it's for. What problem it solves.
          </p>
          <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
            <a href="/signup" class="btn btn-primary btn-lg">Get started free</a>
            <a href="#demo" class="btn btn-ghost btn-lg" style="background:rgba(255,255,255,0.15); border-color:rgba(255,255,255,0.4); color:#fff;">Watch demo</a>
          </div>
          <p style="font-size:0.875rem; opacity:0.7; margin-top:16px;">No credit card required</p>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="section" id="features">
      <div class="container-wide">
        <div class="section-header">
          <h2 class="text-section-heading">Everything you need</h2>
          <p class="text-supporting">Built for teams that ship fast.</p>
        </div>
        <div class="grid-cards">
          <div class="card card-interactive scroll-reveal stagger-1">
            <div class="card-body">
              <div style="font-size:2rem; margin-bottom:16px;">⚡</div>
              <h3 class="text-card-heading">Feature One</h3>
              <p class="text-supporting">Description of the feature and its direct benefit.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section style="padding:96px 0; background:var(--gradient-hero-blue); text-align:center; color:#fff;">
      <div class="container-hero">
        <h2 style="font-family:'Poppins',sans-serif; font-size:2.5rem; font-weight:700; margin-bottom:16px;">Ready to get started?</h2>
        <p style="font-size:1.125rem; opacity:0.9; margin-bottom:32px;">Join thousands of teams already using ProductName.</p>
        <a href="/signup" class="btn btn-lg" style="background:#fff; color:var(--color-primary); border-color:#fff;">Start for free</a>
      </div>
    </section>

  </main>
</body>
</html>
```

---

# PART 19 — SAAS TEMPLATES

## Dashboard Shell

```html
<div class="dashboard-shell">

  <aside class="sidebar dashboard-sidebar">
    <div class="sidebar-logo">
      <a href="/" class="navbar-brand" style="color:var(--color-text-primary);">
        <img src="logo.svg" alt="Logo" style="height:32px;">
        <span style="font-size:1rem;">AppName</span>
      </a>
    </div>
    <nav>
      <span class="sidebar-section-label">Main</span>
      <a href="/dashboard" class="sidebar-nav-item active">📊 Dashboard</a>
      <a href="/analytics"  class="sidebar-nav-item">📈 Analytics</a>
      <a href="/users"      class="sidebar-nav-item">👥 Users</a>
      <span class="sidebar-section-label">Settings</span>
      <a href="/settings"   class="sidebar-nav-item">⚙️ Settings</a>
    </nav>
    <div class="sidebar-footer">
      <div class="sidebar-nav-item" style="cursor:pointer;">
        <div class="avatar" style="width:28px;height:28px;font-size:0.75rem;">JD</div>
        <div>
          <div style="font-size:0.875rem; font-weight:500; color:var(--color-text-primary);">John Doe</div>
          <div class="text-caption">john@example.com</div>
        </div>
      </div>
    </div>
  </aside>

  <header class="topbar dashboard-topbar">
    <div class="topbar-left">
      <div class="topbar-search" role="button" aria-label="Search (⌘K)">
        <span class="topbar-search-text">Search...</span>
        <span class="topbar-search-kbd">⌘K</span>
      </div>
    </div>
    <div class="topbar-right">
      <button class="topbar-icon-btn" aria-label="Notifications">
        🔔 <span class="notification-badge"></span>
      </button>
      <div class="avatar" role="button" aria-label="User menu">JD</div>
    </div>
  </header>

  <main class="dashboard-content" id="main-content">
    <div style="margin-bottom:var(--space-7);">
      <h1 class="text-section-heading" style="margin-bottom:4px;">Dashboard</h1>
      <p class="text-supporting">Welcome back, John. Here's what's happening.</p>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card scroll-reveal stagger-1">
        <span class="kpi-label">Total Revenue</span>
        <div style="display:flex; align-items:flex-end; justify-content:space-between;">
          <span class="kpi-value">$48,295</span>
          <div class="kpi-icon">💰</div>
        </div>
        <div class="kpi-change kpi-change-up">↑ 12.5% from last month</div>
      </div>
      <div class="kpi-card scroll-reveal stagger-2">
        <span class="kpi-label">Active Users</span>
        <div style="display:flex; align-items:flex-end; justify-content:space-between;">
          <span class="kpi-value">2,847</span>
          <div class="kpi-icon">👥</div>
        </div>
        <div class="kpi-change kpi-change-up">↑ 8.1% from last month</div>
      </div>
    </div>

    <div class="data-table-wrapper scroll-reveal">
      <div class="data-table-header">
        <h3 class="text-card-heading">Recent Activity</h3>
        <button class="btn btn-ghost btn-sm">Export</button>
      </div>
      <table class="data-table">
        <thead>
          <tr><th>Name</th><th>Status</th><th>Date</th><th>Amount</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>Example Row</td>
            <td><span class="badge badge-success">Active</span></td>
            <td class="text-caption">Jun 1, 2026</td>
            <td style="font-weight:600; color:var(--color-success);">$1,200</td>
          </tr>
        </tbody>
      </table>
      <div class="data-table-pagination">
        <span>Showing 1–10 of 48 results</span>
        <div style="display:flex; gap:8px;">
          <button class="btn btn-ghost btn-sm">Previous</button>
          <button class="btn btn-primary btn-sm">Next</button>
        </div>
      </div>
    </div>
  </main>
</div>
```

---

# PART 20 — ENTERPRISE TEMPLATES

## Enterprise Data Page

```html
<div class="dashboard-shell">
  <!-- sidebar + topbar same as SaaS template -->
  <main class="dashboard-content">

    <!-- BREADCRUMB -->
    <nav aria-label="Breadcrumb" style="display:flex; align-items:center; gap:8px; margin-bottom:var(--space-5); font-size:0.875rem; color:var(--color-text-secondary);">
      <a href="/dashboard" style="color:var(--color-primary);">Dashboard</a>
      <span aria-hidden="true">/</span>
      <a href="/reports" style="color:var(--color-primary);">Reports</a>
      <span aria-hidden="true">/</span>
      <span style="color:var(--color-text-primary); font-weight:500;" aria-current="page">Q2 2026</span>
    </nav>

    <!-- PAGE HEADER WITH ACTIONS -->
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:var(--space-7);">
      <div>
        <h1 class="text-section-heading" style="margin-bottom:4px;">Q2 2026 Report</h1>
        <p class="text-supporting">April 1 – June 30, 2026</p>
      </div>
      <div style="display:flex; gap:12px;">
        <button class="btn btn-ghost btn-sm">Export CSV</button>
        <button class="btn btn-primary btn-sm">Generate Report</button>
      </div>
    </div>

    <!-- FILTER BAR -->
    <div style="display:flex; gap:12px; margin-bottom:var(--space-6); flex-wrap:wrap;">
      <select class="input" style="width:auto; height:36px; font-size:0.875rem;" aria-label="Filter by region">
        <option>All Regions</option>
        <option>North America</option>
        <option>Europe</option>
      </select>
      <input type="date" class="input" style="width:auto; height:36px; font-size:0.875rem;" aria-label="Start date">
    </div>

    <!-- ENTERPRISE TABLE -->
    <div class="data-table-wrapper">
      <table class="enterprise-table">
        <thead>
          <tr><th>ID</th><th>Department</th><th>Status</th><th>Revenue</th><th>Change</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr>
            <td class="text-mono">#ENT-0042</td>
            <td>Sales</td>
            <td><span class="status-dot status-dot-active" aria-hidden="true"></span>Active</td>
            <td style="font-weight:600;">$284,000</td>
            <td style="color:var(--color-success); font-weight:500;">+8.2%</td>
            <td><button class="btn btn-ghost btn-sm" style="height:28px; padding:4px 10px; font-size:0.8125rem;">View</button></td>
          </tr>
        </tbody>
      </table>
    </div>

  </main>
</div>
```

---

# PART 21 — PERSONAL PROJECT BLUEPRINT

## The Minimum Viable Design System

Copy this into every new project. 10 minutes to set up. Professional results immediately.

### Step 1 — CSS Variables

```css
:root {
  --color-primary: hsl(211, 100%, 50%);
  --color-primary-dark: hsl(211, 100%, 35%);
  --color-primary-ring: rgba(0, 123, 255, 0.4);
  --color-secondary: hsl(208, 7%, 46%);
  --color-success: hsl(122, 39%, 49%);
  --color-warning: hsl(38, 100%, 50%);
  --color-error: hsl(6, 78%, 57%);
  --color-text-primary: #333333;
  --color-text-secondary: #6c757d;
  --color-text-label: #495057;
  --color-text-heading: #343a40;
  --color-text-inverse: #ffffff;
  --color-surface-card: #ffffff;
  --color-surface-subtle: #f8f9fa;
  --color-surface-hover: #e9ecef;
  --color-border-default: #dee2e6;
  --color-border-focus: #206bc4;
  --color-overlay-dark: rgba(0, 0, 0, 0.8);
  --gradient-body: linear-gradient(to right, #ece9e6, #ffffff);
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
  --shadow-xl: 0 16px 40px rgba(0,0,0,0.15);
  --shadow-navbar: 0 2px 4px rgba(0,0,0,0.10);
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 999px;
  --space-2: 8px;   --space-3: 12px;  --space-4: 16px;
  --space-5: 20px;  --space-6: 24px;  --space-7: 32px;
  --space-8: 40px;  --space-10: 64px;
  --duration-normal: 250ms;
  --duration-slow: 450ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

### Step 2 — Base Reset

```css
*, *::before, *::after { box-sizing: border-box; }
html { font-size: 16px; -webkit-font-smoothing: antialiased; }
body { margin: 0; font-family: "Roboto", "Inter", Arial, sans-serif; font-size: 1rem; line-height: 1.6; color: var(--color-text-primary); background: var(--gradient-body); overflow-x: hidden; }
img  { max-width: 100%; height: auto; display: block; }
a    { color: var(--color-primary); }
```

### Step 3 — The 5 Components You Always Need

```css
/* BUTTON */
.btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; font-family:inherit; font-size:1rem; font-weight:600; cursor:pointer; border:2px solid transparent; border-radius:var(--radius-pill); padding:10px 24px; height:44px; transition:all var(--duration-normal) ease; outline:none; text-decoration:none; }
.btn:focus-visible { box-shadow:0 0 0 3px var(--color-primary-ring); }
.btn-primary { background:var(--color-primary); color:#fff; border-color:var(--color-primary); }
.btn-primary:hover { background:var(--color-primary-dark); transform:scale(1.03); }
.btn-ghost { background:#f0f0f0; color:var(--color-primary); border-color:var(--color-primary); }
.btn-ghost:hover { background:var(--color-primary); color:#fff; }
.btn-full { width:100%; }

/* CARD */
.card { background:var(--color-surface-card); border:none; border-radius:var(--radius-xl); overflow:hidden; box-shadow:var(--shadow-md); transition:transform var(--duration-normal) ease, box-shadow var(--duration-normal) ease; }
.card-interactive:hover { transform:translateY(-8px); box-shadow:var(--shadow-xl); }
.card-body { padding:var(--space-6); }

/* INPUT */
.input { display:block; width:100%; height:44px; padding:10px 14px; font-family:inherit; font-size:0.9375rem; color:var(--color-text-primary); background:#fff; border:1.5px solid var(--color-border-default); border-radius:var(--radius-md); outline:none; transition:border-color 0.2s ease, box-shadow 0.2s ease; }
.input:focus { border-color:var(--color-border-focus); box-shadow:0 0 0 3px var(--color-primary-ring); }
.form-label { display:block; font-size:0.875rem; font-weight:500; color:var(--color-text-label); margin-bottom:8px; }
.form-group { margin-bottom:var(--space-5); }

/* NAVBAR */
.navbar { position:fixed; top:0; left:0; right:0; z-index:1000; height:64px; background:var(--color-overlay-dark); box-shadow:var(--shadow-navbar); display:flex; align-items:center; }
.navbar-inner { max-width:1200px; margin:0 auto; padding:0 var(--space-5); width:100%; display:flex; align-items:center; justify-content:space-between; }
.content-offset { padding-top:72px; }

/* SECTION */
.section { padding:60px 0; }
.section-header { text-align:center; margin-bottom:var(--space-8); }
.container-wide { max-width:1200px; margin:0 auto; padding:0 20px; }
.grid-cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:var(--space-6); }
```

### Step 4 — The 3 Rules to Never Break

1. Every async operation shows a loading state within 100ms
2. Every error shows inline feedback — never `alert()`
3. Every interactive element has a hover state and a focus state

### Step 5 — Pre-Launch Quality Check

```
[ ] Tested on mobile (375px)
[ ] All buttons have hover states
[ ] All inputs have focus states
[ ] Loading states exist for all API calls
[ ] Error states exist for all forms
[ ] No content touches the screen edge on mobile
[ ] Contrast ratio passes for all text
[ ] No horizontal scroll
```

---

*This is a living document. Update it as you discover new patterns, better values, and improved techniques. The best design system is the one you actually use.*

---

**ULTIMATE DESIGN BIBLE — Complete**
Parts: 21 | Laws: 45 | Components: 40+ | Templates: 6 | Patterns: 100+
