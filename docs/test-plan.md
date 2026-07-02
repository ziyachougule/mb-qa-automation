# Test Plan — mb.io Marketing Site UI Automation

## Objective

Verify that the public mb.io marketing site correctly renders and links its core
user-facing content — navigation, the spot-trading preview, marketing banners,
app-download entry points, and the company page — and that it degrades sanely at
the edges (unknown routes, mobile viewport), using automated UI tests that run
on every push.

## Scope

### In scope

| Area | Suite | Tests |
|---|---|---|
| Header navigation: all 6 items render, correct destinations, `$MBG` new-tab behavior, desktop viewports (1920×1080, 1366×768) | `tests/test_navigation.py` | 22 |
| Spot-trading preview ("Catch your next trade"): all 3 categories render, grouping invariants, per-row fields (icon, name, price, % change) | `tests/test_trading.py` | 9 |
| Marketing banners (hero + sponsorship, incl. ordering), app-download deep link, QR popover, Why MultiBank page headings | `tests/test_content_links.py` | 13 |
| Edge cases: 404 handling for unknown routes, mobile breakpoint (375×667) nav collapse and menu completeness | `tests/test_edge_cases.py` | 3 |

**Total: 47 automated tests**, all verified green locally and in CI.

### Out of scope (and why)

- **Authenticated trading flows** (orders, balances, deposits/withdrawals) — the
  assignment's `trade.mb.io` target is behind a login wall with no test
  credentials provided; automating account creation against a production
  financial platform is inappropriate without authorization. See README.
- **Exact market data values** — prices and gainer/loser membership are live and
  volatile; tests assert shape and invariants instead.
- **Cross-browser matrix** — chromium is the reference browser for this
  assessment; the pytest-playwright setup extends to firefox/webkit via
  `--browser` when needed.
- **Non-English locales** — content assertions target English; the locale
  *prefix* is handled dynamically (see Environments).

## Approach

- **Playwright + pytest**, Page Object Model: assert-free page objects
  (`pages/`) expose data; tests (`tests/`) own all assertions.
- **Role/text-based locators** over CSS/XPath, so tests survive styling and DOM
  refactors; structural selectors only where the site exposes no accessible name.
- **Live-recon-first**: every locator and expected value was captured from the
  running site before a test was written, and every suite was run twice before
  being considered done (this caught two SPA hydration races).

## Environments

- **System under test**: production `https://mb.io` (no staging available).
  The site force-redirects to a geo-detected locale (`/en-AE` from the Gulf,
  `/en` from US CI runners), so all URL assertions derive the locale at runtime
  from `BasePage.current_locale`.
- **Local**: macOS, Python 3.11+, chromium via `playwright install`.
- **CI**: GitHub Actions (`ubuntu-latest`), runs the full suite on every push
  and pull request, uploads the self-contained HTML report as an artifact even
  on failure.

## Entry / exit criteria

**Entry** (per run): dependencies installed, chromium available, mb.io reachable.

**Exit** (for a change to merge): full suite green in CI, no known flaky tests
(fix or remove in the same change), HTML report artifact produced, README/docs
updated if behavior assumptions changed.

## Deliverables

- Test framework and suites (this repo)
- CI workflow with HTML report artifact (`.github/workflows/tests.yml`)
- This test plan, [risk matrix](risk-matrix.md),
  [release readiness checklist](release-readiness-checklist.md), and
  [QA strategy responses](qa-strategy.md)
