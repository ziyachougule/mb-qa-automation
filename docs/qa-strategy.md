# QA Strategy — Task 2 Written Responses

Answers to the assessment's five QA strategy questions.

## 1. Where do you start?

I'd spend day one figuring out what's real versus assumed. What flows actually
touch money? Is there a staging environment, or are we stuck testing against
production? That last question decides everything else — I can't safely automate
against real user funds without knowing that first.

## 2. How would you approach testing this app?

I'd rank by risk, not by ease. Money flows first — deposits, withdrawals, trades,
balances — tested manually and via API before anything else, because these can't
afford flaky automation hiding a real bug. Then core UI on both iOS and Android,
since platform differences are easy to miss if you only check one. Then edge
cases — low balance, dropped connection mid-transaction, session timeout during
a trade — because that's what real users actually hit. With two weeks, I'm not
trying to automate everything; I'm protecting the highest-risk paths first.

## 3. What does QA look like inside a sprint?

I get involved at ticket creation, not after the build — checking acceptance
criteria are actually testable before the ticket even enters the sprint. During
dev, I pair with engineers on edge cases they might've missed. Once it's built,
I test against the criteria, then regress just the affected area — not the whole
suite every time. Before release, full smoke and regression run, and nothing goes
out with known flaky tests, because a test nobody trusts isn't protecting
anything. For this app, I'd add one more rule: no ticket closes without a QA pass
on both platforms, no exceptions, given how close we are to launch.

## 4. What does your ideal regression suite look like?

Layered. A fast smoke suite — login, balance, trade, deposit/withdrawal — that
runs on every commit, a few minutes max. A fuller regression suite nightly. And
a small set of real end-to-end tests against staging before every release. For
fintech specifically, I'd also check that what the UI shows actually matches the
backend ledger — a UI test can pass while a balance calculation is quietly wrong
underneath. And I'm ruthless about flaky tests — fix them or cut them, same
sprint.

## 5. What would keep you up at night?

Three things. Race conditions on money — someone double-taps withdraw during a
network retry and it processes twice. Platform parity — iOS and Android quietly
diverging on things like biometric auth or what happens to a pending trade when
the app backgrounds. And honestly, the thing I just ran into building this very
assessment: an assumption turning out to be wrong. I found the documented URL for
this challenge led straight to a login wall with nothing public behind it. A
two-week-old app with no QA docs is exactly the kind of place where "staging
mirrors prod" or "test data is realistic" hasn't actually been checked — and you
don't want to find that out during launch week.
