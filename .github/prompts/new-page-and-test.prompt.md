---
description: "Scaffold a new Page Object and matching test file for a given URL path and page description."
---
Create a new Page Object and a matching Pytest test file for the following page:

- **Page name**: ${{PAGE_NAME}}
- **URL path**: ${{URL_PATH}}
- **Key elements and actions** (describe the UI elements to interact with):
  ${{ELEMENTS_AND_ACTIONS}}

Steps:
1. Create `pages/${{PAGE_NAME}}_page.py` inheriting from `BasePage`, with locators and action methods for each element described
2. Create `tests/test_${{PAGE_NAME}}.py` with a `class Test${{PAGE_NAME_PASCAL}}` containing smoke tests for each action
3. Follow the project POM conventions in `.github/instructions/page-objects.instructions.md`
4. Follow the test conventions in `.github/instructions/test-writing.instructions.md`
