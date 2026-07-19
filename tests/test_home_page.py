import pytest
from pages.home_page import HomePage


class TestHomePage:
    """Smoke tests for the home page."""

    def test_page_title_is_not_empty(self, driver):
        page = HomePage(driver)
        page.navigate()
        assert page.get_title() != "", "Page title should not be empty"

    def test_page_url_matches_base(self, driver):
        import os
        page = HomePage(driver)
        page.navigate()
        assert os.getenv("BASE_URL", "https://example.com") in page.get_current_url()

    def test_heading_is_visible(self, driver):
        page = HomePage(driver)
        page.navigate()
        assert page.is_visible(page.HEADING), "Main heading should be visible"
