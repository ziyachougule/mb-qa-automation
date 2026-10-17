import pytest
pytestmark = pytest.mark.regression
from playwright.sync_api import expect

from pages.trading_page import TradingPage


@pytest.fixture
def trading_page(page):
    """TradingPage on the homepage with the spot-pairs section fully loaded.

    The pair rows are hydrated client-side after `load`, so wait for the
    section heading and at least one /explore/ row before yielding.
    """
    trading = TradingPage(page)
    trading.goto()
    expect(page.locator(TradingPage.SPOT_SECTION_HEADING)).to_be_visible()
    expect(page.locator("a[href^='/explore/']").first).to_be_visible()
    return trading


class TestTrading:
    """Spot-pairs preview coverage: section rendering, grouping, row contents."""

    # --- 1. Section renders with all three categories --------------------------
    @pytest.mark.smoke
    def test_spot_section_renders_all_categories(self, trading_page):
        assert trading_page.get_categories() == list(TradingPage.SPOT_CATEGORIES)

    @pytest.mark.parametrize("category", TradingPage.SPOT_CATEGORIES)
    def test_category_displays_trading_pairs(self, trading_page, category):
        pairs = trading_page.get_pairs_in_category(category)
        assert len(pairs) > 0

    # --- 2. Pairs are grouped into the right categories -------------------------

    def test_gainers_and_losers_do_not_overlap(self, trading_page):
        # A pair may legitimately appear in both a gainers/losers list and
        # Trending Now, but it can't be a top gainer and a top loser at once.
        gainers = {p["name"] for p in trading_page.get_pairs_in_category("Top Gainers")}
        losers = {p["name"] for p in trading_page.get_pairs_in_category("Top Losers")}
        assert gainers, "Top Gainers rendered no pairs"
        assert losers, "Top Losers rendered no pairs"
        assert gainers.isdisjoint(losers)

    def test_pairs_are_unique_within_each_category(self, trading_page):
        for category in trading_page.get_categories():
            names = [p["name"] for p in trading_page.get_pairs_in_category(category)]
            assert len(names) == len(set(names)), f"duplicate pair in {category}: {names}"

    # --- 3. Each pair row contains icon, name, price, and % change --------------

    @pytest.mark.parametrize("category", TradingPage.SPOT_CATEGORIES)
    def test_pair_entries_have_expected_fields(self, trading_page, category):
        pairs = trading_page.get_pairs_in_category(category)
        assert pairs, f"{category} rendered no pairs"
        for pair in pairs:
            assert pair["icon"], f"missing icon in {category}: {pair}"
            assert pair["icon"].startswith("https://"), f"icon is not a URL: {pair}"
            assert pair["name"], f"missing name in {category}: {pair}"
            assert pair["price"] and pair["price"].startswith("$"), f"bad price in {category}: {pair}"
            assert pair["change_pct"] and pair["change_pct"].endswith("%"), (
                f"bad change_pct in {category}: {pair}"
            )
