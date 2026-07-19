---
name: test-debugger
description: 'Diagnoses and fixes failing or flaky Selenium tests. Use when: test failing, fix test, flaky test, element not found, locator broken, stale element, timeout error, NoSuchElementException, WebDriverException, debug selenium, test error. Identifies root cause and applies minimal targeted fix.'
argument-hint: 'Paste the failing test name, error message, or traceback'
---

# Test Debugger Skill

Diagnoses and resolves failing Selenium tests with minimal, targeted fixes.

## When to Use
- A test is throwing `NoSuchElementException`, `TimeoutException`, or `StaleElementReferenceException`
- A test passes locally but fails in CI (flaky)
- A locator stopped working after a UI change
- A test produces wrong assertion values

## Procedure

### 1. Collect Information
Read:
1. The failing test file (`tests/test_*.py`)
2. The Page Object(s) used by that test (`pages/*_page.py`)
3. `conftest.py` (fixture setup/teardown)
4. `.env` / `utils/config.py` (BASE_URL, timeouts)

### 2. Classify the Failure

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `NoSuchElementException` | Locator wrong or not waited | Fix locator or add `find()` wait |
| `TimeoutException` | Element never appears | Fix locator; check page loaded |
| `StaleElementReferenceException` | Element re-rendered after find | Re-find inside action; use `find()` not caching element |
| `AssertionError` | Wrong expected value | Update assertion |
| `WebDriverException: session not created` | Driver/browser mismatch | Update webdriver-manager |
| Flaky (passes sometimes) | Race condition | Add explicit wait in Page Object |

### 3. Apply Fix
- **Locator wrong** → update the tuple in the Page Object only
- **Missing wait** → add `self.wait.until(...)` in `BasePage` or override in Page Object
- **Wrong assertion** → fix expected value in test
- **Fixture issue** → fix `conftest.py` setup

### 4. Rules
- **Never** add `time.sleep()` as a fix
- **Never** change test logic unless the logic is wrong
- Fix in Page Object, not in test code, for locator/wait issues
- Prefer CSS selectors over XPath in locator fixes

### 5. Diagnostic Script
Use this snippet in a scratch run to inspect what the driver sees:
```python
# Paste in conftest or a quick debug test
print(driver.page_source[:3000])
print(driver.current_url)
driver.save_screenshot("debug.png")
```

## References
- [Base Page](../../pages/base_page.py)
- [conftest.py](../../conftest.py)
- [Helpers](../../utils/helpers.py)
- [Config Loader](../../utils/config.py)
