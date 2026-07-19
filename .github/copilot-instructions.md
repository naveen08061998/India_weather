# Agentic Automation Testing — Project Guidelines

## Stack
- **Language**: Python 3.x
- **Test framework**: Pytest + Selenium WebDriver
- **Pattern**: Page Object Model (POM)
- **Reporting**: pytest-html, Allure
- **Browser management**: webdriver-manager (auto-downloads drivers)

## Project Structure
```
pages/          # Page Object classes (one file per page)
tests/          # Pytest test files (test_*.py)
utils/          # Shared helpers (screenshots, waits)
reports/        # HTML and Allure test reports (auto-generated)
conftest.py     # Shared fixtures — driver lifecycle, browser options
pytest.ini      # Pytest configuration
.env            # BASE_URL and timeout values (never commit secrets)
```

## Code Conventions
- All Page Objects inherit from `pages/base_page.py`
- Locators are class-level tuples: `LOCATOR = (By.CSS_SELECTOR, "selector")`
- Tests use the `driver` fixture from `conftest.py`; never instantiate WebDriver directly
- Use `BasePage.find()`, `click()`, `type()`, `is_visible()` — never raw `driver.find_element` in tests
- One `class TestXxx` per file; group related scenarios in the same class
- Explicit waits live in `BasePage`; do not use `time.sleep()` in tests

## Build & Test Commands
```bash
# Run all tests (headed Chrome)
.venv\Scripts\pytest

# Run headless
.venv\Scripts\pytest --headless

# Run a specific file
.venv\Scripts\pytest tests/test_home_page.py -v

# Parallel execution (4 workers)
.venv\Scripts\pytest -n 4
```

## Environment
- Copy `.env` and set `BASE_URL` before running
- Virtual environment is `.venv/`; activate with `.venv\Scripts\activate`
