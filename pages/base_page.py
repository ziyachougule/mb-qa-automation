from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

DEFAULT_TIMEOUT_MS = 10_000


class BasePage:
    """Common functionality shared by all page objects."""

    def __init__(self, page: Page):
        self.page = page

    def safe_click(self, selector: str, timeout: int = DEFAULT_TIMEOUT_MS) -> None:
        """Wait for an element to be visible/enabled, then click it."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.click(timeout=timeout)

    def get_text(self, selector: str, timeout: int = DEFAULT_TIMEOUT_MS) -> str:
        """Wait for an element to be visible and return its inner text."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator.inner_text(timeout=timeout)

    def wait_for_load(self, state: str = "networkidle", timeout: int = DEFAULT_TIMEOUT_MS) -> None:
        """Wait for the page to reach a given load state (default: networkidle)."""
        self.page.wait_for_load_state(state, timeout=timeout)

    def is_element_visible(self, selector: str, timeout: int = DEFAULT_TIMEOUT_MS) -> bool:
        """Return True/False for element visibility instead of raising."""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
