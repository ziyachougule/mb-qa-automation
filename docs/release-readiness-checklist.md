# Release Readiness Checklist

Gate for calling a release (or this assessment's deliverable) ready. Every box
must be checked or have a written, accepted exception — "mostly green" is not a
state.

## Test results

- [x] Full suite green in CI on the release commit (48/48 on each of chromium, firefox and webkit; [Actions runs](https://github.com/ziyachougule/mb-qa-automation/actions))
- [x] Full suite green locally, run twice consecutively (guards the SPA hydration races)
- [x] Zero known flaky tests — anything flaky was fixed or cut in the same change, not skipped or retried into passing
- [x] Suite passes in both locale environments (`en-AE` locally, `en` on CI runners)

## Coverage of the highest-risk paths

- [x] All P-High risks in the [risk matrix](risk-matrix.md) have at least one automated test (P1, P2, P4, P5)
- [x] Edge cases covered: 404 handling, mobile breakpoint, new-tab external link
- [x] No assertion depends on volatile live data (prices, gainer/loser membership)

## Artifacts & reproducibility

- [x] HTML report generated and uploaded as a CI artifact, including on failure
- [x] One-command run works from a clean checkout (`pip install -r requirements.txt`, `playwright install`, `pytest`)
- [x] Both `pytest` and `python -m pytest` invocations work (regression from CI run 1)

## Documentation & disclosure

- [x] README current: setup, run commands, test summary, design decisions
- [x] All deviations from the brief disclosed and justified (trade.mb.io login wall → mb.io substitution, flagged section in README)
- [x] Environment surprises documented where the next person will look (geo-locale in README + `base_page.py`; hydration races in test comments)
- [x] docs/ complete: test plan, QA strategy, risk matrix, this checklist

## Known exceptions (accepted)

- **Node 20 deprecation notice** on `actions/*` versions in CI — cosmetic
  annotation, upgrade when GitHub publishes the next major action versions.
- **Live-production dependency** — no staging exists for the marketing site;
  content/campaign changes may fail tests without a code defect. Accepted and
  documented as risk T4.
- **Authenticated flows untested** — out of scope without credentials; see
  test plan. The POM structure extends to post-login flows when access exists.
