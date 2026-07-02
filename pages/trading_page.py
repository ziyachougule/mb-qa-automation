from playwright.sync_api import Page

from pages.base_page import BasePage


class TradingPage(BasePage):
    """Page object for the spot-trading preview on the mb.io marketing home page.

    There is no standalone "trading" page on the marketing site -- the spot
    pairs preview ("Catch your next trade") is a section embedded in the
    /en-AE homepage itself, grouped into three categories (Top Gainers,
    Trending Now, Top Losers). Each row is a link to /explore/{SYMBOL}
    showing an icon, name, price, and % change.
    """

    HOME_URL = "https://mb.io/en-AE"

    SPOT_SECTION_HEADING = "role=heading[name='Catch your next trade']"
    SPOT_CATEGORIES = ("Top Gainers", "Trending Now", "Top Losers")

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> None:
        """Navigate to the mb.io/en-AE homepage and wait for it to load."""
        self.page.goto(self.HOME_URL)
        self.wait_for_load(state="load")

    # --- Spot-pairs preview --------------------------------------------------

    def get_categories(self) -> list[str]:
        """Return which of SPOT_CATEGORIES are currently rendered on the page."""
        return [
            category
            for category in self.SPOT_CATEGORIES
            if self.page.get_by_role("heading", name=category, exact=True).count() > 0
        ]

    def get_pairs_in_category(self, category_name: str) -> list[dict]:
        """Return {icon, name, price, change_pct} for each pair row under `category_name`."""
        card = self.page.locator(f"div:has(> h2:text-is('{category_name}'))").first
        rows = card.locator("a[href^='/explore/']")
        pairs = []
        for i in range(rows.count()):
            row = rows.nth(i)
            icon = row.locator("img").first.get_attribute("src")
            fields = [t.strip() for t in row.inner_text().split("\n") if t.strip()]
            name, price, change_pct = (fields + [None, None, None])[:3]
            pairs.append({"icon": icon, "name": name, "price": price, "change_pct": change_pct})
        return pairs
