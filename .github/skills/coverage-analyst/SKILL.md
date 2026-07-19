---
name: coverage-analyst
description: 'Analyzes test coverage across the automation suite. Use when: coverage report, what is not tested, missing tests, test coverage analysis, untested pages, gaps in automation, which tests are missing. Produces a table of Page Objects vs test coverage and a prioritized list of gaps.'
argument-hint: 'Optional: focus on a specific page or feature area'
---

# Coverage Analyst Skill

Read-only analysis of the automation suite to identify untested pages and methods.

## When to Use
- Sprint planning: deciding what new tests to write
- After adding multiple Page Objects without matching tests
- Auditing the automation suite for gaps
- Reporting automation coverage to stakeholders

## Procedure

### 1. Inventory Page Objects
List all files in `pages/` (excluding `base_page.py` and `__init__.py`).
For each file, extract:
- Class name
- All public methods (excluding `__init__` and `navigate`)

### 2. Inventory Test Files
List all files in `tests/` (only `test_*.py`).
For each file, extract:
- Which Page Object(s) are imported
- Which Page Object methods are called

### 3. Build Coverage Matrix

For each Page Object method, mark:
- ✅ Tested — called by at least one test
- ❌ Not tested — never called in any test file
- ⚠️ Page has no test file at all

### 4. Prioritize Gaps
Rank untested items by risk:
1. **Authentication flows** — highest risk
2. **Form submissions / data mutations**
3. **Navigation / routing**
4. **Display / read-only assertions**

### 5. Output Format

```
## Coverage Summary
| Page Object     | Total Methods | Tested | Coverage |
|----------------|---------------|--------|----------|
| LoginPage       | 4             | 4      | 100%     |
| CheckoutPage    | 6             | 2      | 33%      |

## Pages With No Test File
- DashboardPage → no tests/test_dashboard_page.py found

## Untested Methods
- CheckoutPage.apply_coupon()
- CheckoutPage.remove_item()

## Recommended Next Tests (Prioritized)
1. CheckoutPage — apply_coupon (data mutation, high risk)
2. DashboardPage — full smoke suite missing
```

## Rules
- **Never** write or modify any code
- Only read `pages/` and `tests/` directories
- Do not guess at test coverage — only count explicit method calls

## References
- [pages/](../../pages/)
- [tests/](../../tests/)
- [Test Writing Skill](../skills/test-writer/SKILL.md)
