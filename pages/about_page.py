from playwright.sync_api import Page

from pages.base_page import BasePage


class AboutPage(BasePage):
    """Page object for the "Why MultiBank Group?" company page, reached from
    the home page's "Company" nav item (see HomePage.click_why_multibank).
    """

    ABOUT_URL = "https://mb.io/en-AE/company"

    PAGE_HEADING = "role=heading[name='Why MultiBank Group?']"
    SECTION_HEADINGS = (
        "A tradition of global leadership",
        "Innovation with purpose",
        "Integrity built into every decision",
        "The strength behind MultiBank Group",
        "Community & Media",
        "Corporate",
        "Privacy",
        "Compliance",
    )

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> None:
        """Navigate directly to the Why MultiBank Group company page and wait for it to load."""
        self.page.goto(self.ABOUT_URL)
        self.wait_for_load(state="load")

    # --- Section headings -----------------------------------------------------

    def get_all_section_headings(self) -> list[str]:
        """Return the visible text of every heading on the page."""
        return [h.inner_text().strip() for h in self.page.get_by_role("heading").all()]

    def is_section_present(self, heading_text: str) -> bool:
        """Return True if a heading with this exact text is present on the page."""
        return self.page.get_by_role("heading", name=heading_text, exact=True).count() > 0
