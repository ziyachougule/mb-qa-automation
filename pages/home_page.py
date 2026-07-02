from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    """Page object for the mb.io marketing home page.

    The assignment's original target, https://trade.mb.io/, redirects an
    unauthenticated session straight to /login (no nav, banners, or
    spot-pairs content ever renders there). Everything this page object
    targets -- header nav, marketing banners, the spot-pairs preview, and
    the app-download link -- actually lives on the mb.io marketing site,
    so the suite (including the `base_url` fixture) targets mb.io/en-AE
    instead. See the flagged section in README.md.
    """

    HOME_URL = "https://mb.io/en-AE"

    # --- Header / primary nav ("Main" is the <nav>'s accessible name) ---------
    MAIN_NAV = "role=navigation[name='Main']"
    SIGN_IN_LINK = "role=link[name='Sign in']"
    SIGN_UP_LINK = "role=link[name='Sign up']"
    COMPANY_NAV_LABEL = "Company"  # -> lands directly on the Why MultiBank page

    # The language picker and app-download QR trigger are icon-only buttons
    # with no accessible name (a real a11y gap on the site), so they can only
    # be targeted structurally: index 0 is language, index 1 opens the QR code.
    HEADER_ICON_TRIGGERS = "header [data-slot='popover-trigger']"
    APP_DOWNLOAD_TRIGGER_INDEX = 1

    # --- Hero + marketing banners -----------------------------------------------
    HERO_BANNER_HEADING = "role=heading[name='Crypto for everyone']"
    OPEN_ACCOUNT_CTA = "role=link[name='Open an account']"
    # Real App Store / Google Play smart link (mbio.go.link), found on the
    # hero "Download the app" CTA -- there is no app-store badge in the footer.
    DOWNLOAD_APP_CTA = "[data-button-type='download']"
    SPONSORSHIP_BANNER_HEADING = "role=heading[name='Unblemished. Unstoppable. United.']"

    # --- Spot-pairs preview ("Catch your next trade") ---------------------------
    SPOT_SECTION_HEADING = "role=heading[name='Catch your next trade']"
    SPOT_EXPLORE_ALL_CTA = "role=link[name='Explore all assets']"
    SPOT_CATEGORIES = ("Top Gainers", "Trending Now", "Top Losers")

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> None:
        """Navigate to the mb.io marketing home page and wait for it to load."""
        self.page.goto(self.HOME_URL)
        self.wait_for_load(state="load")

    # --- Nav ---------------------------------------------------------------

    def get_nav_items(self) -> list[tuple[str, str]]:
        """Return (label, href) for every link in the main header nav."""
        links = self.page.locator(self.MAIN_NAV).get_by_role("link")
        items = []
        for i in range(links.count()):
            link = links.nth(i)
            items.append((link.inner_text().strip(), link.get_attribute("href")))
        return items

    def click_nav_item(self, label: str) -> None:
        """Click a main-nav item by its visible label (e.g. 'Company')."""
        self.page.locator(self.MAIN_NAV).get_by_role("link", name=label, exact=True).click()
        self.wait_for_load(state="load")

    # --- Marketing banners / app download -----------------------------------

    def is_hero_banner_visible(self) -> bool:
        return self.is_element_visible(self.HERO_BANNER_HEADING)

    def is_sponsorship_banner_visible(self) -> bool:
        return self.is_element_visible(self.SPONSORSHIP_BANNER_HEADING)

    def get_app_download_link(self) -> str | None:
        """Return the App Store/Google Play smart-link href from the hero CTA."""
        return self.page.locator(self.DOWNLOAD_APP_CTA).get_attribute("href")

    def open_app_download_qr(self) -> None:
        """Open the header popover showing the QR code for the mobile app."""
        self.page.locator(self.HEADER_ICON_TRIGGERS).nth(self.APP_DOWNLOAD_TRIGGER_INDEX).click()

    # --- Spot-pairs preview --------------------------------------------------

    def get_spot_pair_categories(self) -> list[str]:
        """Return which of SPOT_CATEGORIES are currently rendered on the page."""
        return [
            category
            for category in self.SPOT_CATEGORIES
            if self.page.get_by_role("heading", name=category, exact=True).count() > 0
        ]

    def get_spot_pairs(self, category: str) -> list[dict]:
        """Return {symbol, name, price, change_pct} for each pair row under `category`."""
        card = self.page.locator(f"div:has(> h2:text-is('{category}'))").first
        rows = card.locator("a[href^='/explore/']")
        pairs = []
        for i in range(rows.count()):
            row = rows.nth(i)
            href = row.get_attribute("href") or ""
            symbol = href.rsplit("/", 1)[-1]
            fields = [t.strip() for t in row.inner_text().split("\n") if t.strip()]
            name, price, change_pct = (fields + [None, None, None])[:3]
            pairs.append({"symbol": symbol, "name": name, "price": price, "change_pct": change_pct})
        return pairs

    # --- About Us / Why MultiBank --------------------------------------------

    def click_why_multibank(self) -> None:
        """Navigate to the Why MultiBank Group page (About Us) via the Company nav item."""
        self.click_nav_item(self.COMPANY_NAV_LABEL)

    def get_why_multibank_headings(self) -> list[str]:
        """Return all section headings on the Why MultiBank Group page."""
        return [h.inner_text().strip() for h in self.page.get_by_role("heading").all()]
