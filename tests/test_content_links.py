import re

import pytest
pytestmark = pytest.mark.regression
from playwright.sync_api import expect

from pages.about_page import AboutPage
from pages.home_page import HomePage

# App Store / Google Play smart link on the hero "Download the app" CTA.
DOWNLOAD_DEEP_LINK_PATTERN = re.compile(r"^https://mbio\.go\.link/\w+$")

QR_POPOVER_CONTENT = "[data-slot='popover-content']"
QR_POPOVER_TEXT = "Scan the QR code to download the app"

# All headings captured on /en-AE/company during recon (11 total: the page
# title, two paragraph-style sub-headings, and the eight section headings
# tracked in AboutPage.SECTION_HEADINGS).
WHY_MULTIBANK_HEADINGS = [
    "Why MultiBank Group?",
    "For nearly two decades, MultiBank has built a reputation as one of the "
    "world’s most trusted financial institutions. With a foundation rooted in "
    "regulation, transparency, and technological excellence, we continue to "
    "serve millions of clients across the globe with integrity and ambition.",
    "A tradition of global leadership",
    "Innovation with purpose",
    "Integrity built into every decision",
    "The strength behind MultiBank Group",
    "Community & Media",
    "The latest news and discussions about MultiBank Group.",
    "Corporate",
    "Privacy",
    "Compliance",
]


class TestContentLinks:
    """Marketing banners, app-download links, and Why MultiBank page content."""

    # --- 1. Marketing banners render in the expected page region ---------------
    @pytest.mark.smoke
    def test_hero_and_sponsorship_banners_visible(self, page):
        home = HomePage(page)
        home.goto()

        assert home.is_hero_banner_visible()
        assert home.is_sponsorship_banner_visible()

    def test_hero_banner_appears_above_sponsorship_banner(self, page):
        home = HomePage(page)
        home.goto()

        hero = page.locator(HomePage.HERO_BANNER_HEADING)
        sponsorship = page.locator(HomePage.SPONSORSHIP_BANNER_HEADING)
        expect(hero).to_be_visible()
        expect(sponsorship).to_be_visible()
        assert hero.bounding_box()["y"] < sponsorship.bounding_box()["y"]

    # --- 2. App Store / Google Play links resolve correctly --------------------

    def test_download_app_cta_uses_smart_deep_link(self, page):
        home = HomePage(page)
        home.goto()

        href = home.get_app_download_link()
        assert href, "hero 'Download the app' CTA has no href"
        assert DOWNLOAD_DEEP_LINK_PATTERN.match(href), f"unexpected deep link: {href}"

    def test_qr_popover_trigger_present_and_opens(self, page):
        home = HomePage(page)
        home.goto()

        triggers = page.locator(HomePage.HEADER_ICON_TRIGGERS)
        assert triggers.count() > HomePage.APP_DOWNLOAD_TRIGGER_INDEX
        expect(triggers.nth(HomePage.APP_DOWNLOAD_TRIGGER_INDEX)).to_be_visible()

        expect(page.locator(QR_POPOVER_CONTENT)).to_have_count(0)
        home.open_app_download_qr()

        popover = page.locator(QR_POPOVER_CONTENT)
        expect(popover).to_be_visible()
        expect(popover).to_contain_text(QR_POPOVER_TEXT)
        assert popover.locator("img, svg, canvas").count() > 0, "QR popover has no QR image"

    # --- 3. Why MultiBank page renders all expected headings --------------------

    def test_why_multibank_page_has_all_expected_headings(self, page):
        about = AboutPage(page)
        about.goto()
        expect(page.locator(AboutPage.PAGE_HEADING)).to_be_visible()

        actual = about.get_all_section_headings()
        missing = [h for h in WHY_MULTIBANK_HEADINGS if h not in actual]
        assert not missing, f"missing headings: {missing}"

    @pytest.mark.parametrize("section", AboutPage.SECTION_HEADINGS)
    def test_why_multibank_section_present(self, page, section):
        about = AboutPage(page)
        about.goto()
        expect(page.locator(AboutPage.PAGE_HEADING)).to_be_visible()

        assert about.is_section_present(section)
