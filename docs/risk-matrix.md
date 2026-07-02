# Risk Matrix

Risks are scored Likelihood × Impact (High / Medium / Low). The top section
covers product risks the suite guards against; the bottom covers risks *to the
test effort itself* — several of which materialized during this assessment and
are marked accordingly.

## Product risks

| # | Risk | Likelihood | Impact | Mitigation / coverage |
|---|---|---|---|---|
| P1 | Nav destinations break or drift (rename, wrong href, dead route) — users can't reach signup, support, or the token site | Medium | High | 22 navigation tests: every item's href and click-through URL asserted, `$MBG` new-tab behavior verified |
| P2 | Spot-pairs preview renders empty or miscategorized (a "top gainer" shown as a loser) — misleading financial info on the front page | Medium | High | Grouping invariants: gainers ∩ losers = ∅, no duplicates per category, every row has icon/name/price/% change |
| P3 | Unknown routes soft-404 (HTTP 200) or silently redirect home — dead links get indexed, users get no error indication | Low | Medium | 404 test asserts real 404 status, preserved path, "Page not found" heading, recovery link |
| P4 | Mobile nav regression — hamburger disappears or the sheet drops an item, stranding mobile users (the majority on marketing sites) | Medium | High | Mobile tests assert hamburger presence, zero horizontal overflow, and all 6 items in the opened sheet with correct hrefs |
| P5 | App-download funnel breaks (dead deep link, broken QR popover) — lost installs at the primary conversion point | Low | High | Deep-link pattern asserted on the hero CTA; QR popover opened and verified to contain the code image |
| P6 | Desktop/mobile content divergence — nav items added to one component but not the other (they are separate components) | Medium | Medium | Mobile-sheet items asserted against the same `NAV_ITEMS` source of truth as desktop |

## Risks to the test effort

| # | Risk | Likelihood | Impact | Status / mitigation |
|---|---|---|---|---|
| T1 | **Documented target has no testable surface** — `trade.mb.io` redirects unauthenticated users to `/login` | — | High | **Materialized.** Verified by live recon, flagged to the recruiter, suite retargeted to the public `mb.io` marketing site (README, flagged section) |
| T2 | **Environment-dependent behavior** — geo-detected locale rewrites every URL (`/en-AE` locally, `/en` in CI) | — | High | **Materialized** (as 12 CI failures). All URL assertions now derive the locale at runtime via `BasePage.current_locale` |
| T3 | **SPA hydration races** — URL updates after `click()` returns; pair rows populate after `load` | — | Medium | **Materialized** (as local flakes). Auto-retrying `expect()` assertions; fixture waits for hydrated content before reads |
| T4 | Testing against production: content/campaign changes (e.g. sponsorship banner ends) fail tests without a code bug | Medium | Medium | Volatile values asserted by shape/invariant, not exact value; content changes surface as explicit, explainable failures |
| T5 | Live market data volatility breaks exact-value assertions | High | Low | No exact prices/percentages asserted anywhere |
| T6 | Accessibility gaps limit robust locators (icon-only header buttons have no accessible name) | — | Low | **Materialized.** Structural fallback selectors used only there, documented in `home_page.py` as a real a11y finding |
| T7 | Site availability/latency causes transient CI failures | Low | Medium | Auto-retrying assertions absorb slowness; a one-off `goto` timeout observed once locally and confirmed non-reproducible (6/6 clean retries) |
