import pytest

# pytest-playwright provides `page`, `browser`, `context`, etc. as built-in
# fixtures. We only override `base_url` here so relative page.goto() calls
# resolve against the site under test without needing --base-url on the CLI.
#
# This is mb.io/en-AE, not the assignment's trade.mb.io: that host redirects
# unauthenticated visitors straight to /login with no public content, so the
# suite targets the public marketing site instead (see the flagged section
# in README.md). Page objects currently navigate with absolute URLs, so this
# fixture is a default for future relative navigations, not a dependency.


@pytest.fixture(scope="session")
def base_url():
    return "https://mb.io/en-AE"


# TODO: add custom fixtures here (e.g. authenticated_page, test data loaders)
