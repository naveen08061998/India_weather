"""
Utility helpers for the test suite.
"""
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def take_screenshot(driver, name: str, folder: str = "reports/screenshots"):
    """Save a screenshot to the given folder."""
    os.makedirs(folder, exist_ok=True)
    timestamp = int(time.time())
    path = os.path.join(folder, f"{name}_{timestamp}.png")
    driver.save_screenshot(path)
    return path


def wait_for_url_contains(driver, text: str, timeout: int = 10):
    """Wait until the current URL contains the given text."""
    WebDriverWait(driver, timeout).until(EC.url_contains(text))
