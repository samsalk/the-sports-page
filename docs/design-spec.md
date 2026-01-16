# The Sports Page - Design Specification

## Typography Scale

Using a modular scale with base 14px and ratio ~1.25 for clear visual hierarchy.

### Screen Typography

| Level | Size | rem | Use | Font |
|-------|------|-----|-----|------|
| 1 | 42px | 3rem | Masthead title | Oswald (sans) |
| 2 | 24px | 1.75rem | League headers (NHL, NBA, EPL) | Oswald (sans) |
| 3 | 16px | 1.125rem | Section headers (Yesterday's Scores, Standings) | Oswald (sans) |
| 4 | 14px | 1rem | Conference/Category headers (Eastern, Goals) | Oswald (sans) |
| 5 | 13px | 0.9rem | Division headers, game scores | Merriweather (serif) |
| 6 | 12px | 0.85rem | Body text (standings rows, leader lists) | Merriweather (serif) |
| 7 | 11px | 0.75rem | Secondary info (box scores, schedule) | Merriweather (serif) |
| 8 | 10px | 0.7rem | Tertiary info (game status, timestamps) | Merriweather (serif) |

### Print Typography

Scaled down proportionally for dense single-page layout.

| Level | Size | Use |
|-------|------|-----|
| 1 | 1.25rem | Masthead title |
| 2 | 0.9rem | League headers |
| 3 | 0.7rem | Section headers |
| 4 | 0.6rem | Conference/Category headers |
| 5 | 0.55rem | Division headers, game scores |
| 6 | 0.5rem | Body text |
| 7 | 0.45rem | Secondary info |
| 8 | 0.4rem | Tertiary info |

---

## Color Palette

```css
--newsprint-bg: #f4f1ea;    /* Warm paper background */
--text-primary: #1a1a1a;     /* Near-black for body text */
--text-secondary: #4a4a4a;   /* Gray for secondary info */
--border-light: #d0d0d0;     /* Subtle dividers */
--border-heavy: #000;        /* Bold dividers, emphasis */
--accent: #c41e3a;           /* Highlight color (unused currently) */
```

---

## Font Families

| Variable | Fonts | Use |
|----------|-------|-----|
| `--font-serif` | Merriweather, Georgia, serif | Body text, standings, data |
| `--font-sans` | Oswald, Franklin Gothic, Arial Narrow, sans-serif | Headlines, labels |
| `--font-mono` | Courier New, monospace | Scores, statistics, tabular data |

---

## Component Hierarchy

### Page Structure
```
Masthead (Level 1)
  └── Tagline, Date (Level 7)

League Section (Level 2: "NHL")
  ├── Yesterday's Scores (Level 3)
  │     └── Game Cards (Level 5: scores, Level 8: status)
  │           └── Box Score (Level 7, Level 8 for details)
  │
  ├── Standings (Level 3)
  │     └── Conference (Level 4: "Eastern")
  │           └── Division (Level 5: "Atlantic")
  │                 └── Team Rows (Level 6)
  │
  ├── Leaders (Level 3)
  │     └── Category (Level 4: "Goals")
  │           └── Player Rows (Level 6)
  │
  └── Schedule (Level 3)
        └── Game Entries (Level 7, Level 8 for times)
```

---

## Box Score Hierarchy

The box score should maintain clear information hierarchy:

1. **Line Score Table** (Level 6) - Period-by-period scoring, most prominent
2. **Shots on Goal** (Level 7) - Single line summary
3. **Top Scorers** (Level 7) - Two columns by team
   - Team Label (Level 6, bold)
   - Player Stats (Level 8)
4. **Goalies** (Level 7) - Save percentages
   - Goalie Stats (Level 8)

---

## Spacing Scale

| Name | Size | Use |
|------|------|-----|
| xs | 0.25rem | Tight padding (table cells) |
| sm | 0.5rem | Component internal spacing |
| md | 1rem | Between related elements |
| lg | 1.5rem | Between sections |
| xl | 2rem | Major section breaks |

---

## Print Optimizations

- **Target**: Single letter-size page
- **Margins**: 0.3in top/bottom, 0.4in left/right
- **Columns**:
  - Games: 4-column grid
  - Standings: 2-column grid
  - Leaders: 3-column grid
- **Page breaks**: Avoid breaking within games, standings divisions, leader categories
- **Headers**: Always keep with following content

---

## Responsive Breakpoints

| Breakpoint | Columns |
|------------|---------|
| > 900px | 3 columns (games), 2 columns (standings) |
| 600-900px | 2 columns (games), 1 column (standings) |
| < 600px | 1 column (all) |
