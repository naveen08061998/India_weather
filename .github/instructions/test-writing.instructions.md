---
description: "Use when creating or editing Pytest test files for Selenium. Enforces driver fixture usage, POM imports, and test structure conventions. Applies to all test files."
applyTo: "tests/**/*.py"
---
# Pytest Test Conventions

- **Never** instantiate `WebDriver` directly — always use the `driver` fixture from `conftest.py`
- Import Page Objects from `pages/`, not from `tests/`
- Structure: one `class TestXxx` per file, methods start with `test_`
- Follow **Arrange → Act → Assert** within each test method
- **Never** use `time.sleep()` — rely on Page Object waits
- Use descriptive method names: `test_login_redirects_to_dashboard`
- One logical assertion per test where possible; use `pytest.mark` for grouping:
  ```python
  @pytest.mark.smoke
  def test_homepage_loads(self, driver):
      ...
  ```
- Fixtures needed beyond `driver` should be added to `conftest.py`, not defined inline
