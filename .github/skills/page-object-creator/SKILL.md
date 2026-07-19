---
name: page-object-creator
description: 'Creates a new Selenium Page Object class following the project POM conventions. Use when: adding a new page to the automation suite, creating page class, writing page object, adding locators, scaffolding a new page. Generates BasePage-inheriting class with locator tuples, action methods, and a navigate() entry point. Saves to pages/<name>_page.py.'
argument-hint: 'Describe the page: name, URL path, and key elements/actions'
---

# Page Object Creator Skill

Creates a complete, convention-compliant Page Object for any application page.

## When to Use
- Adding a new page to the test automation suite
- Generating locators and action wrappers for a page you just discovered
- Refactoring a test that uses raw `driver.find_element` calls

## Procedure

### 1. Gather Requirements
Collect (from the user or context):
- Page name (e.g. `LoginPage`, `CheckoutPage`)
- URL path (e.g. `/login`, `/checkout/summary`)
- UI elements to interact with (inputs, buttons, links, messages)

### 2. Read the Base Class
Always read [pages/base_page.py](../../pages/base_page.py) before generating code to confirm the available method signatures.

### 3. Generate the File
Use the template below. Save to `pages/<snake_case_name>_page.py`.

#### Template
```python
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class <PascalCaseName>Page(BasePage):
    """Page Object for <description>."""

    # ── Locators ──────────────────────────────────────────
    ELEMENT_NAME = (By.CSS_SELECTOR, "selector")

    def navigate(self):
        self.open("<url_path>")

    # ── Actions ───────────────────────────────────────────
    def action_name(self, value: str):
        self.type(self.ELEMENT_NAME, value)
        self.click(self.SUBMIT_BUTTON)

    # ── Queries ───────────────────────────────────────────
    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MSG)

    def is_success_visible(self) -> bool:
        return self.is_visible(self.SUCCESS_BANNER)
```

### 4. Locator Selection Priority
1. `By.ID` — most stable
2. `By.CSS_SELECTOR` with data attribute: `[data-testid='submit']`
3. `By.CSS_SELECTOR` with semantic selector: `button[type='submit']`
4. `By.NAME` for form fields
5. `By.XPATH` — last resort only

### 5. Rules
- **Never** call `self.driver.find_element(...)` directly
- **Never** use `time.sleep()`
- Group locators at the top of the class as class-level tuples
- Keep action methods at the business level (e.g., `submit_login()`, not `click_button()`)

## References
- [Base Page](../../pages/base_page.py)
- [Example Page Object](../../pages/home_page.py)
- [Page Object Instructions](../instructions/page-objects.instructions.md)
