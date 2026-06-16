# UI_GUIDELINES.md
# UI/UX Design System — Medi AI Platform (Enterprise SaaS Edition)

> Reference this file before generating any component, page, or layout style.
> STRICT RULE: Avoid all generic "AI-generated" visual tropes (no glowing purple backgrounds, no neon gradients, and absolutely no sparkle or magic wand icons). The platform must look like a professional, human-built healthcare SaaS dashboard (e.g., Stripe, Linear, or Epic Systems).

---

## 1. Design Philosophy

- **Clinical-Grade Clarity**: Information must be clean and readable at a glance with zero decorative noise.
- **Enterprise SaaS Aesthetic**: Light, clean, solid layouts utilizing crisp borders and subtle depth over heavy shadows.
- **Dashboard-First, Chat-Second**: The center of the workspace belongs to the structured patient data grid. The AI interaction layer must be anchored in a clean, secondary collapsible panel or bottom block, functioning as an utility tool rather than a chatbot gimmick.
- **Explicit Human Copywriting**: Interface text must use dry, precise, professional actions (e.g., "Upload Lab Report", "View Reference Range Deviation") instead of exaggerated AI phrasing (e.g., "Generate Magic Insights Now").

---

## 2. Iconography Framework

- **Forbidden Icons**: Never use sparkles (`✨`), magic wands, or sci-fi lightning bolts.
- **Permitted Icons**: Use clean, geometric line icons from professional libraries like **Lucide** or **Heroicons**:
  - `Activity` or `HeartPulse` for lab metrics and diagnostics.
  - `FileText` or `FileDigit` for processed document entries.
  - `ShieldAlert` or `AlertCircle` for semantic critical range alerts.
  - `User` or `IdCard` for administrative patient information modules.

---

## 3. Tokenized Color System (High-Contrast Slate)

### Primary Action Framework (Trustworthy Corporate Blue)
```css
:root {
  --color-primary-50:  #F0F6FF;
  --color-primary-100: #E0EFFF;
  --color-primary-200: #B9DDFF;
  --color-primary-500: #0284C7;   /* Main Corporate CTA buttons & Active Elements */
  --color-primary-600: #0369A1;   /* Component Hover Actions */
  --color-primary-700: #075985;   /* Component Pressed/Active States */
}
```

### Semantic Lab Values & Alert Ranges (EHR Standard)
```css
:root {
  --color-success:  #16A34A;   /* Normal laboratory range / Low Risk */
  --color-warning:  #D97706;   /* Borderline metrics / Moderate Risk */
  --color-danger:   #DC2626;   /* Critical values requiring medical view / High Risk */
  --color-info:     #2563EB;   /* System notifications / Extracted document metadata */
}
```

### Neutral Theme Configurations (Solid Fills, No Blurs/Glass)

#### ☀️ Light Mode Layouts
```css
:root {
  --color-bg-primary:    #FFFFFF;
  --color-bg-secondary:  #F8FAFC;   /* Crisp, light grey slate background */
  --color-bg-tertiary:   #F1F5F9;
  --color-border:        #E2E8F0;   /* Ultra-thin structural lines */
  --color-border-strong: #CBD5E1;
  --color-text-primary:  #0F172A;   /* Deep charcoal for maximum readability */
  --color-text-secondary:#475569;
  --color-text-muted:    #94A3B8;
}
```

#### 🌙 Dark Mode Layouts
```css
[data-theme="dark"] {
  --color-bg-primary:    #0B0F19;
  --color-bg-secondary:  #151B26;
  --color-bg-tertiary:   #1E2638;
  --color-border:        #262F45;
  --color-border-strong: #384563;
  --color-text-primary:  #F8FAFC;
  --color-text-secondary:#94A3B8;
  --color-text-muted:    #64748B;
}
```

---

## 4. Typography & Sizing Scales

### Font Framework
- **Standard UI Prose**: `'Inter', system-ui, -apple-system, sans-serif;`
- **Lab Values & Numbers**: `'JetBrains Mono', monospace;` *(Ensures tabular decimals align vertically without layout shifting).*

### Proportional Sizing Controls
```css
--text-xs:   0.75rem  / 1.0rem line-height;  /* Context Badges, Table Headers */
--text-sm:   0.875rem / 1.25rem;             /* Input Field Captions, System Details */
--text-base: 1.000rem / 1.50rem;             /* Standard RAG Prose Output Content */
--text-lg:   1.125rem / 1.75rem;             /* Component Section / Card Headers */
--text-xl:   1.250rem / 1.75rem;             /* Structural Context Groups */
--text-2xl:  1.500rem / 2.00rem;             /* Report View Titles */
```

---

## 5. Spacing & Grid Blueprint (Bento Layout Core)

All element parameters scale strictly according to a clean 4px baseline system (`space-4` = 16px, `space-6` = 24px).

```css
/* Page Wrapper Capping */
.page-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Master Platform Grid Layout (Data First) */
.dashboard-grid {
  display: grid;
  grid-template-columns: 260px 1fr; /* Fixed EHR Sidebar Nav + Workspace */
  gap: 24px;
}

/* Bento Block Interface Pattern */
.bento-card-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}
```

---

## 6. Component Blueprints

### Bento Dashboard Cards (Solid, Crisp Metric Enclosures)
```css
.bento-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px; /* Professional tighter corners over overly rounded bubbles */
  padding: 24px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* Subtle shadow anchor */
}

/* No glowing effects on hover. Use clean, classic elevation shifts */
.bento-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
```

### Action Controls & Buttons
*   **Primary Action Key**: `background: var(--color-primary-500); color: #FFFFFF; font-weight: 500; border-radius: 6px;`
*   **Secondary Boundary Elements**: `background: var(--color-bg-primary); border: 1px solid var(--color-border-strong); color: var(--color-text-primary);`
*   **Alert/Danger Interface Elements**: `background: #FEF2F2; color: var(--color-danger); border: 1px solid #FCA5A5;`

### Laboratory Status Badges
```css
/* Tighter, medical-chart-style badges instead of capsule pills */
.badge-low      { background: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; padding: 2px 8px; border-radius: 4px; }
.badge-moderate { background: #FFFBEB; color: #92400E; border: 1px solid #FEF3C7; padding: 2px 8px; border-radius: 4px; }
.badge-high     { background: #FEF2F2; color: #991B1B; border: 1px solid #FEE2E2; padding: 2px 8px; border-radius: 4px; }
```
