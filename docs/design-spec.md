# The Sports Page - Design Specification

## Typography Scale

Using a modular scale with base 14px and ratio ~1.25 for clear visual hierarchy.

### Screen Typography

| Level | Size | rem | Use | Font |
|-------|------|-----|-----|------|
| 1 | 42px | 3rem | Masthead title | Oswald (sans) |
| 2 | 24px | 1.75rem | League headers (NHL, NBA, MLB) | Oswald (sans) |
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

### NHL / NBA Box Scores

Compact format for hockey and basketball:

1. **Line Score Table** (Level 6) - Period/quarter-by-quarter scoring
2. **Shots on Goal** (Level 7, NHL only) - Single line summary
3. **Top Scorers** (Level 7) - Two columns by team
   - Team Label (Level 6, bold)
   - Player Stats (Level 8)
4. **Goalies** (Level 7, NHL only) - Save percentages

---

## Baseball Box Score Specification

Baseball box scores follow the traditional newspaper format with full batting and pitching tables.

### Structure

```
┌─────────────────────────────────────────────────────────────┐
│ AWAY TEAM NAME                                              │
│ Team  1  2  3  4  5  6  7  8  9   R   H   E                │
│ TOR   0  0  2  0  0  0  4  0  0   6  11   0                │
│ BOS   0  1  0  0  0  0  0  0  1   2   6   0                │
├─────────────────────────────────────────────────────────────┤
│ TORONTO                          BOSTON                     │
│ Batting     AB  R  H BI BB SO    Batting     AB  R  H BI BB SO │
│ Bichette dh  4  0  1  1  0  0    Turner ss    4  1  2  0  0  1 │
│ ...                              ...                        │
│ Totals      35  6 11  6  3  7    Totals      33  2  6  2  2  8 │
├─────────────────────────────────────────────────────────────┤
│ Pitching    IP  H  R ER BB SO    Pitching    IP  H  R ER BB SO │
│ Bieber W    5.1 4  1  1  1  3    Sale L      6.0 8  4  4  2  5 │
│ ...                              ...                        │
├─────────────────────────────────────────────────────────────┤
│ HR: Guerrero (7). 2B: Clement, Muncy. SB: none. DP: 2.     │
└─────────────────────────────────────────────────────────────┘
```

### Line Score Format

Classic horizontal format with inning-by-inning runs:

| Element | Style |
|---------|-------|
| Team abbreviation | Bold, monospace |
| Inning scores | Monospace, right-aligned |
| R/H/E headers | Bold |
| R/H/E values | Bold totals |

Example:
```
       1  2  3  4  5  6  7  8  9    R   H   E
TOR    0  0  2  0  0  0  4  0  0    6  11   0
BOS    0  1  0  0  0  0  0  0  1    2   6   0
```

### Batting Table Columns

| Column | Header | Width | Align | Description |
|--------|--------|-------|-------|-------------|
| Name | (none) | auto | left | Player name + position (e.g., "Bichette dh") |
| AB | AB | 3ch | right | At-bats |
| R | R | 2ch | right | Runs scored |
| H | H | 2ch | right | Hits |
| BI | BI | 2ch | right | Runs batted in (RBI) |
| BB | BB | 2ch | right | Walks |
| SO | SO | 2ch | right | Strikeouts |

- **Totals row**: Bold, appears at bottom
- **Position notation**: Lowercase after name (ss, 2b, cf, dh, etc.)
- **Substitutes**: Can show with hyphen if entering mid-game

### Pitching Table Columns

| Column | Header | Width | Align | Description |
|--------|--------|-------|-------|-------------|
| Name | (none) | auto | left | Pitcher name + result (W/L/S) + record |
| IP | IP | 4ch | right | Innings pitched (e.g., "5.1") |
| H | H | 2ch | right | Hits allowed |
| R | R | 2ch | right | Runs allowed |
| ER | ER | 2ch | right | Earned runs |
| BB | BB | 2ch | right | Walks |
| SO | SO | 2ch | right | Strikeouts |

- **Decision notation**: After name (e.g., "Bieber W, 12-4" or "Sale L, 8-5")
- **Save/Hold**: "S" or "H" for relievers

### Game Notes Section

Compact summary of notable plays:

| Category | Format | Example |
|----------|--------|---------|
| Home Runs | HR: Player (season total) | HR: Guerrero (7), Judge 2 (42) |
| Doubles | 2B: Player, Player | 2B: Clement, Muncy |
| Triples | 3B: Player | 3B: none |
| Stolen Bases | SB: Player | SB: Turner (23) |
| Double Plays | DP: count | DP: 2 |
| Left on Base | LOB: Team count, Team count | LOB: TOR 7, BOS 5 |

### Typography for Baseball

| Element | Level | Font | Weight |
|---------|-------|------|--------|
| Line score | 6 | Monospace | Normal, bold for totals |
| Table headers | 7 | Sans (Oswald) | Bold |
| Player names | 7 | Serif | Normal |
| Statistics | 7 | Monospace | Normal |
| Totals row | 7 | Monospace | Bold |
| Game notes | 8 | Serif | Normal |

### Layout Options

**Full width (single game focus):**
- Both teams side-by-side
- Batting tables in 2 columns
- Pitching tables in 2 columns
- Game notes full width below

**Compact (multi-game page):**
- Batting tables stacked (away then home)
- Narrower columns
- Abbreviated headers if needed

### Print Considerations

- Box scores should not break across pages
- Use `break-inside: avoid` on game container
- Minimum font size: 8px for legibility
- Consider hiding less critical columns (BB, SO) if space constrained

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
