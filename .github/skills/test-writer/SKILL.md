---
name: test-writer
description: 'Writes new Pytest test cases for Selenium automation. Use when: create test, add test case, write test, new test file, add scenario, test coverage. Generates tests using the driver fixture, Page Objects, and Arrange-Act-Assert structure. Saves to tests/test_<feature>.py.'
argument-hint: 'Feature or page to test, and scenarios to cover'
---

# Test Writer Skill

Generates well-structured Pytest test classes for Selenium automation.

## When to Use
- Writing tests for a newly created Page Object
- Adding regression tests for a bug fix
- Expanding scenario coverage for an existing page

## Procedure

### 1. Read Context
Before writing:
- Read `conftest.py` for available fixtures
- Read the target Page Object(s) from `pages/`
- Read `utils/config.py` for credentials/config access

### 2. Generate the Test File
Save to `tests/test_<feature>.py`. Use the template below.

#### Template
```python
import pytest
from pages.<name>_page import <Name>Page
from utils.config import cfg   # use cfg.TEST_USER_EMAIL etc. for credentials


class Test<Name>:
    """Tests for <page description>."""

    def test_<action>_<expected_result>(self, driver):
        # Arrange
        page = <Name>Page(driver)
        page.navigate()

        # Act
        page.<action>(cfg.TEST_USER_EMAIL, cfg.TEST_USER_PASSWORD)

        # Assert
        assert page.is_<condition>_visible(), "<failure message>"
```

### 3. Test Naming Convention
`test_<action>_<expected_outcome>`
Examples:
- `test_login_with_valid_credentials_redirects_to_dashboard`
- `test_login_with_wrong_password_shows_error`
- `test_empty_search_shows_validation_message`

### 4. Pytest Marks
Apply marks at class or method level as needed:
```python
@pytest.mark.smoke          # critical happy-path tests
@pytest.mark.regression     # edge cases / bug-fix tests
@pytest.mark.skip(reason="WIP")
```

### 5. Rules
- **Never** instantiate `WebDriver` directly — always use `driver` fixture
- **Never** import from `tests/` — only from `pages/` and `utils/`
- **Never** use `time.sleep()`
- Credentials come from `cfg` (never hardcode secrets in test files)
- One logical assertion per test method where possible

## References
- [conftest.py](../../conftest.py)
- [Example Test](../../tests/test_home_page.py)
- [Config Loader](../../utils/config.py)
- [Test Writing Instructions](../instructions/test-writing.instructions.md)
