# UI_GUIDELINES.md
# UI/UX Design System — AI Medical Record Intelligence Platform

> Reference this file before generating any component, page, or style.
> All AI agents must follow these rules to maintain visual consistency.

---

## 1. Design Philosophy

- **Medical-grade clarity**: information must be readable at a glance, no visual noise
- **Premium but calm**: not flashy — clean, confident, trustworthy
- **Data-forward**: charts, values, and risk scores are the hero — UI supports them
- **Accessible first**: every design decision must pass WCAG 2.1 AA

---

## 2. Color Palette

### Primary (Brand)
```css
--color-primary-50:  #EEF2FF;
--color-primary-100: #E0E7FF;
--color-primary-200: #C7D2FE;
--color-primary-400: #818CF8;
--color-primary-500: #6366F1;   /* primary action */
--color-primary-600: #4F46E5;   /* hover state */
--color-primary-700: #4338CA;   /* pressed state */
```

### Semantic
```css
--color-success:  #10B981;   /* normal range, low risk */
--color-warning:  #F59E0B;   /* borderline values */
--color-danger:   #EF4444;   /* high risk, critical values */
--color-info:     #3B82F6;   /* informational, AI response */
```

### Neutrals (Light Mode)
```css
--color-bg-primary:    #FFFFFF;
--color-bg-secondary:  #F9FAFB;
--color-bg-tertiary:   #F3F4F6;
--color-border:        #E5E7EB;
--color-border-strong: #D1D5DB;
--color-text-primary:  #111827;
--color-text-secondary:#6B7280;
--color-text-muted:    #9CA3AF;
```

### Neutrals (Dark Mode)
```css
--color-bg-primary:    #0F1117;
--color-bg-secondary:  #1A1D27;
--color-bg-tertiary:   #22263A;
--color-border:        #2D3147;
--color-border-strong: #3D4266;
--color-text-primary:  #F9FAFB;
--color-text-secondary:#9CA3AF;
--color-text-muted:    #6B7280;
```

### Risk Score Colors
```css
--risk-low:      #10B981;   /* 0–40% risk */
--risk-moderate: #F59E0B;   /* 41–70% risk */
--risk-high:     #EF4444;   /* 71–100% risk */
```

---

## 3. Typography

### Font Stack
```css
font-family: 'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif;
font-family-mono: 'JetBrains Mono', 'Fira Code', monospace; /* code blocks */
```

### Scale
```css
--text-xs:   0.75rem  / 1.0rem  line-height  /* labels, badges */
--text-sm:   0.875rem / 1.25rem              /* body small, captions */
--text-base: 1rem     / 1.5rem               /* body default */
--text-lg:   1.125rem / 1.75rem              /* card titles */
--text-xl:   1.25rem  / 1.75rem              /* section headers */
--text-2xl:  1.5rem   / 2rem                 /* page titles */
--text-3xl:  1.875rem / 2.25rem              /* dashboard hero numbers */
--text-4xl:  2.25rem  / 2.5rem               /* landing hero */
```

### Weights
```
400 — body text, descriptions
500 — labels, card titles, nav items
600 — section headers, important values
700 — page titles, risk scores, CTAs
```

### Rules
- Never use font weight below 400
- Risk scores and lab values always use `font-weight: 700` and monospace variant
- Heading hierarchy: h1 → h2 → h3 — never skip levels
- Max line length: 72ch for prose, unrestricted for data tables

---

## 4. Spacing System

Base unit: `4px`

```
space-1:  4px
space-2:  8px
space-3:  12px
space-4:  16px
space-5:  20px
space-6:  24px
space-8:  32px
space-10: 40px
space-12: 48px
space-16: 64px
space-20: 80px
space-24: 96px
```

### Rules
- Card internal padding: `space-6` (24px)
- Section gap: `space-8` (32px) minimum
- Inline element gap: `space-2` or `space-3`
- Page horizontal padding: `space-6` mobile, `space-8` tablet, `space-12` desktop
- Never use arbitrary pixel values — always use scale tokens

---

## 5. Grid System

```css
/* Page container */
max-width: 1280px;
margin: 0 auto;
padding: 0 var(--space-6);

/* Dashboard grid */
grid-template-columns: 240px 1fr;         /* sidebar + content */
gap: var(--space-6);

/* Card grid */
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
gap: var(--space-4);

/* Breakpoints */
--bp-sm:  640px
--bp-md:  768px
--bp-lg:  1024px
--bp-xl:  1280px
--bp-2xl: 1536px
```

---

## 6. Component Rules

### Cards
```
background: var(--color-bg-primary)
border: 1px solid var(--color-border)
border-radius: 12px
padding: 24px
box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)
```

Hover state:
```
box-shadow: 0 4px 12px rgba(0,0,0,0.08)
transform: translateY(-1px)
transition: all 200ms ease
```

### Buttons

Primary:
```
background: var(--color-primary-500)
color: white
border-radius: 8px
padding: 10px 20px
font-weight: 500
transition: background 150ms ease
hover: background var(--color-primary-600)
active: background var(--color-primary-700) + scale(0.98)
```

Secondary:
```
background: transparent
border: 1px solid var(--color-border-strong)
color: var(--color-text-primary)
hover: background var(--color-bg-secondary)
```

Danger:
```
background: #FEF2F2
color: var(--color-danger)
border: 1px solid #FECACA
hover: background #FEE2E2
```

### Badges / Pills
```
border-radius: 9999px
padding: 2px 10px
font-size: var(--text-xs)
font-weight: 500

/* Risk variants */
.badge-low      { background: #ECFDF5; color: #065F46; }
.badge-moderate { background: #FFFBEB; color: #92400E; }
.badge-high     { background: #FEF2F2; color: #991B1B; }
```

### Input Fields
```
border: 1px solid var(--color-border)
border-radius: 8px
padding: 10px 14px
font-size: var(--text-base)
background: var(--color-bg-primary)
focus: border-color var(--color-primary-500) + ring 2px primary-200
placeholder: var(--color-text-muted)
```

### Upload Zone
```
border: 2px dashed var(--color-border-strong)
border-radius: 12px
padding: 48px 32px
text-align: center
background: var(--color-bg-secondary)
cursor: pointer

drag-active:
  border-color: var(--color-primary-500)
  background: var(--color-primary-50)
  transition: all 200ms ease
```

---

## 7. Animation & Transitions

### Timing Tokens
```css
--duration-fast:   100ms
--duration-normal: 200ms
--duration-slow:   350ms
--duration-enter:  400ms
--ease-default:    cubic-bezier(0.4, 0, 0.2, 1)
--ease-spring:     cubic-bezier(0.34, 1.56, 0.64, 1)
--ease-out:        cubic-bezier(0, 0, 0.2, 1)
```

### Standard Transitions
- Button hover/active: `150ms ease`
- Card hover lift: `200ms ease`
- Page route transition: `300ms ease-out`
- Modal/drawer open: `350ms cubic-bezier(0.34,1.56,0.64,1)`
- Toast notifications: `400ms ease`

### Micro-animations
- Upload success: checkmark draw animation (SVG stroke-dashoffset)
- Risk score: count-up number animation on mount
- SHAP bars: slide-in from left on mount (stagger 50ms per bar)
- Chat response: typewriter stream (handled by SSE/streaming API)
- Skeleton loader: shimmer pulse at `1.5s` infinite

### Performance Rules
- Always use `transform` and `opacity` — never animate `width`, `height`, `top`, `left`
- Every animation must have `prefers-reduced-motion` override:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  }
  ```
- Use `will-change: transform` only on elements that are actively animating
- Remove `will-change` after animation completes

---

## 8. Loading States

### Skeleton Pattern
All data-fetching components must render a skeleton before data arrives:
```
ReportCard skeleton: 3 gray rounded bars at 100%, 60%, 40% width
Dashboard skeleton: 4 metric cards + 2 chart placeholders
Chat skeleton: alternating left/right message bubbles
```

Skeleton style:
```css
background: linear-gradient(90deg, var(--color-bg-tertiary) 25%,
  var(--color-border) 50%, var(--color-bg-tertiary) 75%);
background-size: 200% 100%;
animation: shimmer 1.5s infinite;
border-radius: 6px;
```

### Loading Spinner
Use for: file upload processing, OCR running, model inference
```
Size: 24px default, 40px page-level
Color: var(--color-primary-500)
Stroke width: 2.5px
```

---

## 9. Responsive Design

### Breakpoint Behavior

| Screen | Sidebar | Grid | Font scale |
|---|---|---|---|
| Mobile (<768px) | Hidden (hamburger) | 1 column | 90% |
| Tablet (768–1024px) | Collapsible | 2 columns | 95% |
| Desktop (>1024px) | Fixed 240px | 3–4 columns | 100% |

### Mobile-First Rules
- Write base styles for mobile, add `@media (min-width: ...)` for larger screens
- Touch targets minimum: 44×44px
- No hover-only interactions on touch screens
- Sidebar collapses to bottom nav on mobile (4 icons: Dashboard, Upload, Chat, Profile)

---

## 10. Dark / Light Mode

- Use CSS custom properties exclusively — no hardcoded colors
- Implement via `[data-theme="dark"]` on `<html>` element
- System preference detected via `prefers-color-scheme` on first load
- User preference stored in localStorage key: `theme`
- All charts must have dark-mode variants (use Recharts `theme` prop)
- Charts background: `var(--color-bg-secondary)` always

---

## 11. Accessibility (WCAG 2.1 AA)

- Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text
- All interactive elements have visible `:focus-visible` ring
- All images have meaningful `alt` text
- Form inputs linked to labels via `htmlFor` / `id`
- Error messages announced via `aria-live="polite"`
- Modals trap focus and restore on close
- Skip-to-content link at top of every page
- Icon-only buttons must have `aria-label`
- Risk scores communicated via text, not color alone

---

## 12. Visual Hierarchy Rules

1. Most important: risk score / primary metric — largest, highest contrast
2. Second: extracted lab values — tabular, mono font
3. Third: entity tags — small pills, muted colors
4. Fourth: metadata (date, filename) — smallest, muted color
5. Actions (upload, chat) — primary button style, always visible
6. Destructive actions (delete) — danger style, never default position

---

## 13. Page-Specific UI Requirements

### Dashboard
- Top row: 4 metric cards (Total Reports, Avg Risk, Latest Upload, Chat Sessions)
- Middle: Recent Reports grid (card per report)
- Right panel (desktop): Quick health summary

### Report Detail `/reports/[id]`
- Hero: filename + upload date + overall risk badge
- Section 1: Extracted lab values in a clean 2-column grid
- Section 2: Risk prediction card with SHAP bar chart
- Section 3: Detected entities as color-coded pills
- Section 4: Raw extracted text (collapsible, monospace)

### Chat `/chat`
- Left: report selector dropdown
- Right: chat window (WhatsApp-style bubbles)
- Bottom: input + send button
- AI messages: left-aligned, light blue background
- User messages: right-aligned, primary color background

### Upload `/upload`
- Full-page centered upload zone
- Progress bar during upload
- Processing steps shown in real time: OCR → NLP → Embedding → Done
