import pytest
import json
from pathlib import Path
from playwright.sync_api import expect

from pages.home_page import HomePage

# (label, href template) as rendered in the main nav. mb.io force-redirects
# to the geo-detected locale (en-AE locally, en on CI runners), so internal
# hrefs are templates filled in with the locale actually served — see
# BasePage.current_locale. $MBG is the only external item (absolute URL,
# opens in a new tab).
_NAV_DATA_FILE = Path(__file__).resolve().parent.parent / "test-data" / "nav_items.json"

with _NAV_DATA_FILE.open(encoding="utf-8") as f:
    NAV_ITEMS = [(item["label"], item["href"]) for item in json.load(f)]
NAV_LABELS = [label for label, _ in NAV_ITEMS]
INTERNAL_NAV_ITEMS = [(label, href) for label, href in NAV_ITEMS if href.startswith("/")]

DESKTOP_VIEWPORTS = [(1920, 1080), (1366, 768)]


class TestNavigation:
    """Main-nav coverage: presence, destinations, and desktop viewport behavior."""

    # --- 1. All expected nav items render and are visible ---------------------

    @pytest.mark.parametrize("label", NAV_LABELS)
    def test_nav_item_is_visible(self, page, label):
        home = HomePage(page)
        home.goto()

        link = page.locator(HomePage.MAIN_NAV).get_by_role("link", name=label, exact=True)
        assert link.is_visible()

    # --- 2. Each nav item links to the correct destination ---------------------

    @pytest.mark.parametrize("label, expected_href", NAV_ITEMS)
    def test_nav_item_href(self, page, label, expected_href):
        home = HomePage(page)
        home.goto()

        nav_items = dict(home.get_nav_items())
        assert nav_items[label] == expected_href.format(locale=home.current_locale)

    @pytest.mark.parametrize("label, expected_path", INTERNAL_NAV_ITEMS)
    def test_internal_nav_item_click_navigates(self, page, label, expected_path):
        home = HomePage(page)
        home.goto()

        expected = "https://mb.io" + expected_path.format(locale=home.current_locale)
        home.click_nav_item(label)
        # Client-side (SPA) routing: the URL can update a beat after click()
        # returns, so use an auto-retrying assertion instead of a bare check.
        expect(page).to_have_url(expected)

    def test_mbg_nav_item_opens_new_tab(self, page, context):
        home = HomePage(page)
        home.goto()

        with context.expect_page() as popup_info:
            page.locator(HomePage.MAIN_NAV).get_by_role("link", name="$MBG", exact=True).click()
        popup = popup_info.value
        popup.wait_for_load_state()

        assert popup.url.startswith(
            ("https://token.multibankgroup.com", "https://token.mb.io")
        )

    # --- 3. Nav behaves correctly at standard desktop viewport sizes -----------

    @pytest.mark.parametrize("width, height", DESKTOP_VIEWPORTS)
    def test_nav_items_visible_at_desktop_viewport(self, page, width, height):
        page.set_viewport_size({"width": width, "height": height})
        home = HomePage(page)
        home.goto()

        for label in NAV_LABELS:
            link = page.locator(HomePage.MAIN_NAV).get_by_role("link", name=label, exact=True)
            assert link.is_visible()

    @pytest.mark.parametrize("width, height", DESKTOP_VIEWPORTS)
    def test_nav_item_click_navigates_at_desktop_viewport(self, page, width, height):
        page.set_viewport_size({"width": width, "height": height})
        home = HomePage(page)
        home.goto()

        expected = f"https://mb.io/{home.current_locale}/company"
        home.click_nav_item("Company")
        expect(page).to_have_url(expected)
