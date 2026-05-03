# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This project exists so a kid can learn to read sports scores instead of asking Alexa. That origin shapes every product decision:

- **The newspaper format is intentional and pedagogical** — it teaches sports vocabulary (standings columns, box score rows, stat categories) through a familiar, structured layout, not through an app UI
- **Daily refresh at 6 AM is a feature, not a limitation** — this is a morning read; playoff series and final scores are always complete by then
- **Legibility over density** — when adding UI, label things clearly; a child learning to follow sports needs context, not just abbreviations
- **The playoff bracket is high-value** — brackets are intuitive for kids and communicate playoff stakes better than standings do
- **Print-first is real** — the page is actually printed; `print.css` is not an afterthought

When making design or feature decisions, ask whether the change helps someone learn to follow sports over coffee, not whether it's technically interesting.

## Commands

```bash
./run.sh                            # Fetch fresh data + serve at http://localhost:8000
python3 backend/fetch_data.py       # Fetch data only → writes data/sports_data.json
python3 -m http.server 8000         # Serve static site (run from repo root, NOT from a frontend/ subdir)
python3 scripts/test_apis.py        # Smoke-test API connectivity
```

There is no test suite (`backend/tests/` is empty), no linter, and no build step. The frontend is plain HTML/CSS/JS served as static files.

The Python backend uses `requests`, `python-dateutil`, and `pytz` (see `backend/requirements.txt`). `nba_api` is not currently in requirements despite the README — `backend/apis/nba.py` calls the NBA stats API directly via `requests`.

## Architecture

This is a **static site driven by a single JSON file**. The Python backend's only job is to produce `data/sports_data.json`; the browser fetches that file and renders everything client-side. There is no live API call from the browser.

### Data flow

1. `backend/fetch_data.py` is the orchestrator. It loops over five league modules in `backend/apis/` (`mlb`, `nhl`, `nba`, `epl`, `nfl`), calls each one's `fetch_all_data(yesterday_date)`, and writes a single JSON file to `data/sports_data.json` at the repo root.
2. Each league module is independent and must return the same shape: `{yesterday, standings, leaders, schedule}`. Failures are isolated per league — `fetch_data.py` catches exceptions and substitutes `create_error_structure()` so one broken API doesn't take down the page.
3. `js/app.js` fetches `data/sports_data.json` on `DOMContentLoaded`, loads user prefs from localStorage (`js/storage.js`), and hands both to `renderer.js` which builds the DOM.
4. League visibility and "Show Box Scores" are pure client-side toggles that re-render from the already-fetched JSON.

### Where things live (note: paths differ from README)

The README and `start.sh` describe a `frontend/` subdirectory, but the **actual layout has `css/`, `js/`, `data/`, and `index.html` at the repo root**. `backend/config.py` also points at a stale `frontend/data/` path and is not used by `fetch_data.py` — `fetch_data.py` writes to `<repo_root>/data/`. Treat `backend/config.py` as dead code unless you intentionally rewire it.

- `index.html` — single page, loads CSS in order: `base` → `newspaper` → `components` → `print` (print-only).
- `css/` — cascade matters: `base.css` defines CSS variables and reset, `newspaper.css` is layout/typography, `components.css` is per-component, `print.css` is print-media-only overrides.
- `js/` — loaded as plain `<script>` tags (no modules, no bundler) in this order: `storage.js`, `utils.js`, `renderer.js`, `app.js`. Functions are defined on the global scope and called across files.

### Adding or changing a league

To add a league: create `backend/apis/<league>.py` exposing `fetch_all_data(yesterday_date)` returning the standard shape; import and call it in `fetch_data.py` (wrapped in the same try/except pattern); add a `<input type="checkbox" id="toggle-<league>">` to `index.html`; extend rendering in `js/renderer.js`. The `renderer.js` `hasBoxScoreData()` helper already branches on league-specific box-score shapes (NHL goalies/shots, MLB innings/batting, EPL goals) — new sports may need a new branch there.

## Automated data updates

`.github/workflows/update-data.yml` runs `fetch_data.py` daily (10:00 and 11:00 UTC to cover EDT/EST 6 AM) and commits `data/sports_data.json` back to the repo via `stefanzweifel/git-auto-commit-action`. This is why the JSON file is checked in — the site is deployed via GitHub Pages and the committed JSON *is* the production data. When you see "Update sports data [automated]" commits on `main`, that's this workflow.

The EPL fetch needs the `FOOTBALL_DATA_API_KEY` secret (free key from football-data.org); NHL/NBA/MLB/NFL APIs are keyless. Locally, put the key in `.env` (see `.env.example`).

## Design system

Typography uses an 8-level scale defined in `docs/design-spec.md`. When adding UI, pick the appropriate level rather than introducing new sizes — the print stylesheet has matching scaled-down values per level, and breaking the scale will break the print layout.
