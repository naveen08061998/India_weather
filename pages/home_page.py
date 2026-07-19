from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for the application home page."""

    # Locators
    HEADING = (By.TAG_NAME, "h1")
    NAV_LINKS = (By.CSS_SELECTOR, "nav a")
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def navigate(self):
        self.open("/")

    def get_heading(self) -> str:
        return self.get_text(self.HEADING)

    def search(self, keyword: str):
        self.type(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
