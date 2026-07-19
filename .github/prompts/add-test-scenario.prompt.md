---
description: "Add a new test scenario to an existing Page Object and test file."
---
Add a new test scenario to the existing automation suite:

- **Page**: ${{PAGE_NAME}} (`pages/${{PAGE_NAME}}_page.py`)
- **Scenario to test**: ${{SCENARIO_DESCRIPTION}}
- **Expected outcome**: ${{EXPECTED_OUTCOME}}

Steps:
1. Read `pages/${{PAGE_NAME}}_page.py` to understand existing locators and methods
2. If new UI elements are needed, add locators and action methods to the Page Object
3. Add a new `test_` method to `tests/test_${{PAGE_NAME}}.py` covering the scenario
4. Method name should describe the scenario: `test_<action>_<expected_result>`
5. Follow Arrange → Act → Assert structure
