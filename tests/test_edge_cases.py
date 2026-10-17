from urllib.parse import urljoin

import pytest
pytestmark = pytest.mark.regression
from playwright.sync_api import expect
from pytest_playwright.pytest_playwright import page

from pages.home_page import HomePage
from tests.test_navigation import NAV_ITEMS

INVALID_ROUTE = "https://mb.io/en-AE/this-route-does-not-exist"

MOBILE_VIEWPORT = {"width": 375, "height": 667}  # iPhone SE

MOBILE_MENU_TRIGGER = "role=button[name='Open menu']"


class TestEdgeCases:
    """Failure-mode coverage: bad routes and the mobile breakpoint."""
    @pytest.mark.smoke
    def test_invalid_route_shows_not_found_state(self, page):
        """Guards against broken 404 handling on unknown routes.

        Real-world failure modes this catches: the SPA router crashing or
        rendering a blank shell on an unmatched path (user sees a white
        screen), the server answering 200 for junk URLs (soft-404s that get
        indexed by search engines), and a silent redirect to the homepage
        that leaves the user with no indication their link was dead.
        """
        response = page.goto(INVALID_ROUTE)

        # Server must answer with a real 404, not a soft 200 (the status
        # survives mb.io's geo-locale redirect, e.g. /en-AE/* -> /en/*).
        assert response is not None and response.status == 404

        # No silent redirect to home: the bad path stays in the address bar
        # (only the locale prefix may be rewritten by geo-detection).
        assert "this-route-does-not-exist" in page.url

        # A proper not-found page renders, with a recovery path back home.
        expect(page.get_by_role("heading", name="Page not found")).to_be_visible()
        expect(page.get_by_role("link", name="Back to Homepage")).to_be_visible()

        # Not a blank/crashed shell: header nav and footer content still render.
        assert len(page.locator("body").inner_text().strip()) > 100

    def test_mobile_viewport_collapses_nav_into_menu(self, page):
        """Guards against layout regressions at the mobile breakpoint.

        Real-world failure modes this catches: a CSS/breakpoint change that
        leaves the desktop nav rendered on small screens (overflowing or
        overlapping the header), the hamburger trigger disappearing so
        mobile users lose navigation entirely, and content spilling past
        the viewport edge forcing horizontal scroll.
        """
        page.set_viewport_size(MOBILE_VIEWPORT)
        home = HomePage(page)
        home.goto()

        # Desktop nav is gone; the hamburger trigger replaces it.
        expect(page.locator(HomePage.MAIN_NAV)).to_have_count(0)
        expect(page.locator(MOBILE_MENU_TRIGGER)).to_be_visible()

        # No layout breakage: the page must not overflow horizontally.
        overflow = page.evaluate(
            "document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        assert overflow == 0, f"page overflows viewport horizontally by {overflow}px"

    def test_mobile_menu_exposes_all_nav_items(self, page):
        """Guards against nav items being dropped from the mobile menu.

        The desktop nav and mobile sheet are separate components, so a nav
        item added to one can silently be missing from the other — mobile
        users (the majority on marketing sites) would simply never see that
        section. Asserts the opened sheet exposes all six nav items with
        the same destinations the desktop nav links to.
        """
        page.set_viewport_size(MOBILE_VIEWPORT)
        home = HomePage(page)
        home.goto()

        page.locator(MOBILE_MENU_TRIGGER).click()
        sheet = page.get_by_role("dialog")
        expect(sheet).to_be_visible()

        for label, href in NAV_ITEMS:
            expected = href.format(locale=home.current_locale)
            link = sheet.get_by_role("link", name=label, exact=True)
            expect(link).to_be_visible()
            assert link.get_attribute("href") == expected, f"{label} points at wrong destination"
    
    def test_nav_links_are_not_broken(self, page):
        """Guards against dead navigation entries.
        
        Real-world failure mode: a page gets renamed or removed and the nav still
        points at it, so users hit a 404 from the most prominent element on the site.
        Only 404 and 5xx count as broken. 401/403 from external hosts is usually bot
        protection, not a dead link, so it would cause false failures.
    """
        home = HomePage(page)
        home.goto()

        broken = []
        for label, href in home.get_nav_items():
            url = urljoin(page.url, href)
            response = page.request.get(url, timeout=30000)
            if response.status == 404 or response.status >= 500:
                broken.append(f"{label} -> {url} ({response.status})")

        assert not broken, f"Broken navigation links: {broken}"