# Test Plan — mb.io Marketing Site UI Automation

## Objective

Verify that the public mb.io marketing site correctly renders and links its core
user-facing content — navigation, the spot-trading preview, marketing banners,
app-download entry points, and the company page — and that it degrades sanely at
the edges (unknown routes, mobile viewport, broken nav links), using automated UI tests that run
on every push.

## Scope

### In scope

| Area | Suite | Tests |
|---|---|---|
- [x] Edge cases covered: 404 handling, mobile breakpoint, broken-link detection across navigation links
| Spot-trading preview ("Catch your next trade"): all 3 categories render, grouping invariants, per-row fields (icon, name, price, % change) | `tests/test_trading.py` | 9 |
| Marketing banners (hero + sponsorship, incl. ordering), app-download deep link, QR popover, Why MultiBank page headings | `tests/test_content_links.py` | 13 |
| Edge cases: 404 handling for unknown routes, mobile breakpoint (375×667) nav collapse and menu completeness, broken-link detection across navigation links | `tests/test_edge_cases.py` | 4 |

**Total: 48 automated tests**, all verified green locally and in CI on chromium, firefox and webkit.

### Out of scope (and why)

- **Authenticated trading flows** (orders, balances, deposits/withdrawals) — the
  assignment's `trade.mb.io` target is behind a login wall with no test
  credentials provided; automating account creation against a production
  financial platform is inappropriate without authorization. See README.
- **Exact market data values** — prices and gainer/loser membership are live and
  volatile; tests assert shape and invariants instead.
- **Real devices and native apps** — mobile behaviour is covered by viewport
  emulation (375×667) only; real-device and native iOS/Android testing is
  outside this web suite.
- **Non-English locales** — content assertions target English; the locale
  *prefix* is handled dynamically (see Environments).

## Approach

The full suite runs on chromium, firefox and webkit, both locally (`--browser`) and in CI as a matrix job with one report per browser. Fast critical-path checks are tagged `smoke`; everything is tagged `regression`.

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
- **Local**: macOS, Python 3.11+, browsers via `playwright install` (chromium by default; firefox and webkit with `--browser`).
- **CI**: GitHub Actions (`ubuntu-latest`), runs the full suite on every push
  and pull request, uploads the self-contained HTML report as an artifact even
  on failure.

## Entry / exit criteria

**Entry** (per run): dependencies installed, target browsers available, mb.io reachable.

**Exit** (for a change to merge): full suite green in CI, no known flaky tests
(fix or remove in the same change), HTML report artifact produced, README/docs
updated if behavior assumptions changed.

## Deliverables

- Test framework and suites (this repo)
- CI workflow with HTML report artifact (`.github/workflows/tests.yml`)
- This test plan, [risk matrix](risk-matrix.md),
  [release readiness checklist](release-readiness-checklist.md), and
  [QA strategy responses](qa-strategy.md)
