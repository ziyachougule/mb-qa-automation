# mb-qa-automation

UI test automation for the **MultiBank.io crypto marketing site**, built with **Playwright + pytest** (Python) on the Page Object Model.

**Base URL under test: `https://mb.io/en-AE`** — covering the main navigation, the spot-trading preview ("Catch your next trade"), marketing banners, app-download links, the Why MultiBank Group company page, 404 handling, and the mobile breakpoint.

**Task 2 answers:** see [docs/qa-strategy.md](docs/qa-strategy.md).

---

## ⚠️ Important: why the target is `mb.io/en-AE`, not `trade.mb.io`

The assignment's original target, `https://trade.mb.io/`, **redirects unauthenticated visitors straight to `/login`** — no navigation, banners, trading pairs, or any other public content ever renders there. This was verified via live recon with Playwright at the start of the project and **flagged to the recruiter**.

All the features the assignment describes (header nav, spot-pairs preview grouped into Top Gainers / Trending Now / Top Losers, marketing banners, company page) actually live on the public marketing site, so the framework targets **`https://mb.io/en-AE`** instead. No login or account creation is used anywhere in the suite.

---

## Prerequisites

- Python **3.11+**
- Install dependencies and browsers:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Running the suite

```bash
pytest --html=reports/report.html
```

(`pytest` alone also works — `pytest.ini` already configures the HTML report path.)

### Viewing the report

Open `reports/report.html` in any browser (it's self-contained, no server needed):

```bash
open reports/report.html   # macOS
```

CI (`.github/workflows/tests.yml`) runs the suite on every push/PR and uploads the same report as a build artifact — even on failure, which is when you need it.

## Test summary — 47 tests across 4 files

| File | Tests | Covers |
|---|---|---|
| `tests/test_navigation.py` | 22 | All 6 nav items render, link to the correct destinations (`$MBG` opens a new tab), and behave at 1920×1080 / 1366×768 |
| `tests/test_trading.py` | 9 | Spot-pairs section renders all 3 categories; pairs are grouped correctly; every row has icon, name, price, % change |
| `tests/test_content_links.py` | 13 | Hero + sponsorship banners render in order; app-download deep link and QR popover work; all 11 Why MultiBank headings present |
| `tests/test_edge_cases.py` | 3 | Unknown routes return a real 404 with a recovery link; nav collapses to a hamburger sheet at 375×667 exposing all 6 items |

All tests were verified green against the live site (two consecutive runs per file).

## Framework & design decisions

**Page Object Model** — locators and page interactions live in `pages/` (`HomePage`, `TradingPage`, `AboutPage`, all extending `BasePage`); tests hold only assertions. When the site's markup changes, the fix lands in one page class instead of across dozens of tests. Page objects are deliberately **assert-free** (getters return data; tests decide what's correct).

**Role/text-based locators over CSS/XPath** — elements are targeted by accessible role and visible text (`get_by_role("heading", name="Top Gainers")`, `role=link[name='Sign in']`), which survives styling and DOM refactors that break class-based selectors. The site uses Tailwind with viewport-unit utility classes (`text-[4.806vw]`…) that are effectively unusable as selectors anyway. Structural selectors are used only where the site offers no accessible name (e.g. the icon-only header popover triggers — a genuine a11y gap, noted in the code).

**Two SPA hydration races found and fixed during verification:**
1. *Client-side routing lag* — after clicking a nav item, `page.url` sometimes hadn't updated by the time `click()` returned, failing bare `assert page.url == …` checks intermittently. Fixed with Playwright's auto-retrying `expect(page).to_have_url(…)`.
2. *Late-hydrating trading pairs* — the spot-pairs rows populate client-side after the `load` event, so reading them immediately can return an empty list. Fixed with a fixture that waits for the section heading and the first `/explore/` row before any test reads data.

**Top Gainers / Top Losers vs Trending Now overlap nuance** — live recon showed a pair can legitimately appear in both a gainers/losers list *and* Trending Now (MultiBank Group did, during development). So the grouping test does **not** assert all three categories are pairwise disjoint — the real invariant is that **Top Gainers and Top Losers never share a pair**, plus no duplicates within a category.

**Other notable behaviors encoded in tests** — the mobile "Open menu" button is removed from the DOM while the sheet is open (tests assert on the opened dialog, not the trigger); the app-download CTA is asserted against the `https://mbio.go.link/<id>` deep-link *pattern*, not the exact campaign ID, which may rotate.

## Assumptions

- **Target URL substitution**: `mb.io/en-AE` stands in for `trade.mb.io` (see the flagged section above).
- **Geo-dependent locale**: mb.io force-redirects every request to the locale it geo-detects for the client (`/en-AE/…` from the Gulf, `/en/…` from GitHub's CI runners) — even explicitly requested locales are rewritten. Discovered when the first CI run failed on hard-coded `en-AE` URLs; all URL/href assertions are now locale-aware (built from `BasePage.current_locale` at runtime).
- **No authentication**: no login or account creation is exercised; everything tested is publicly reachable.
- **Live-site dependency**: tests run against production, so market data (prices, which pairs are gainers/losers) is asserted by *shape and invariants*, not exact values. Content changes (e.g. a sponsorship campaign ending) will surface as legitimate failures.
- **Chromium** is the reference browser locally and in CI.

## Folder structure

```
├── .github/workflows/tests.yml   # CI: pytest on push/PR, uploads HTML report artifact
├── pages/                        # Page Object Model classes
│   ├── base_page.py              #   shared waits/clicks/visibility helpers
│   ├── home_page.py              #   nav, banners, app download, spot-pairs preview
│   ├── trading_page.py           #   "Catch your next trade" categories & pair rows
│   └── about_page.py             #   Why MultiBank Group page headings
├── tests/                        # Test suites (assertions live here only)
│   ├── test_navigation.py
│   ├── test_trading.py
│   ├── test_content_links.py
│   └── test_edge_cases.py
├── fixtures/conftest.py          # shared pytest/Playwright fixtures
├── test-data/                    # static test data (nav_items.json)
├── docs/                         # test plan, QA strategy, risk matrix, release checklist
├── reports/                      # HTML test report output
├── pytest.ini                    # test discovery + report config
└── requirements.txt
```
