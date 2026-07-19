---
description: "Use when creating or editing Page Object files. Enforces BasePage inheritance, locator tuple format, and no raw driver calls. Applies to all files in pages/."
applyTo: "pages/**/*.py"
---
# Page Object Conventions

- Always inherit from `BasePage`: `class XxxPage(BasePage)`
- Locators are **class-level tuples** at the top of the class:
  ```python
  SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
  ```
- Use only `BasePage` methods in action/query methods:
  - `self.find(LOCATOR)` — wait for element presence
  - `self.click(LOCATOR)` — wait for clickable, then click
  - `self.type(LOCATOR, text)` — clear + send keys
  - `self.is_visible(LOCATOR)` — returns bool
  - `self.get_text(LOCATOR)` — returns `.text`
- **Never** call `self.driver.find_element(...)` directly in Page Objects
- **Never** use `time.sleep()` — all waits are handled by `BasePage`
- Each Page Object has a `navigate()` method: `self.open("/path")`
