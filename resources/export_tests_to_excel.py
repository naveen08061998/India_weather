"""
Export all Pytest test cases to a formatted Excel workbook.

Output: reports/test_cases.xlsx
Columns: #, File, Class, Test Method, Use Case ID, Title, Pre-conditions, Steps, Marks
"""

import ast
import re
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import (
    Alignment, Border, Font, PatternFill, Side
)
from openpyxl.utils import get_column_letter

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
TESTS_DIR = ROOT / "tests"
OUT_PATH  = ROOT / "reports" / "test_cases.xlsx"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── colour palette ────────────────────────────────────────────────────────────
HEADER_FILL  = PatternFill("solid", fgColor="0070C0")  # HP blue
ALT_FILL     = PatternFill("solid", fgColor="DDEEFF")  # light blue row
WHITE_FILL   = PatternFill("solid", fgColor="FFFFFF")

HEADER_FONT  = Font(bold=True, color="FFFFFF", size=10, name="Calibri")
BODY_FONT    = Font(size=9, name="Calibri")
BOLD_FONT    = Font(bold=True, size=9, name="Calibri")

THIN  = Side(style="thin",  color="AAAAAA")
THICK = Side(style="medium", color="0070C0")
THIN_BORDER  = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
THICK_BORDER = Border(left=THICK, right=THICK, top=THICK, bottom=THICK)

WRAP = Alignment(wrap_text=True, vertical="top")
CTR  = Alignment(horizontal="center", vertical="top")


# ── helpers ───────────────────────────────────────────────────────────────────

def _marks_from_decorator(dec) -> list[str]:
    """Extract pytest mark names from a decorator node."""
    marks = []
    if isinstance(dec, ast.Attribute):
        marks.append(dec.attr)
    elif isinstance(dec, ast.Call):
        func = dec.func
        if isinstance(func, ast.Attribute):
            marks.append(func.attr)
    return marks


def _parse_docstring(raw: str) -> tuple[str, str, str, str]:
    """Return (uc_id, title, preconditions, steps) from a method docstring."""
    if not raw:
        return "", "", "", ""

    lines = [ln.rstrip() for ln in raw.strip().splitlines()]

    # first non-empty line → "UC-XXX-NNN: Title" or just "Title"
    first = lines[0].strip() if lines else ""
    uc_match = re.match(r"(UC-[\w-]+)\s*[:–-]\s*(.*)", first)
    if uc_match:
        uc_id, title = uc_match.group(1), uc_match.group(2).strip()
    else:
        uc_id, title = "", first

    # split remaining text into sections
    body = "\n".join(lines[1:]).strip()

    pre_match   = re.search(r"Pre-conditions?:(.*?)(?=Steps?:|$)", body, re.DOTALL | re.IGNORECASE)
    steps_match = re.search(r"Steps?:(.*?)(?=TestRail|Assert|$)",  body, re.DOTALL | re.IGNORECASE)

    preconditions = pre_match.group(1).strip()   if pre_match   else ""
    steps         = steps_match.group(1).strip() if steps_match else ""

    # clean leading dashes/numbers from each step line
    def _clean(block: str) -> str:
        cleaned = []
        for ln in block.splitlines():
            ln = ln.strip()
            if ln:
                cleaned.append(re.sub(r"^[\-\d\.\)]+\s*", "", ln))
        return "\n".join(cleaned)

    return uc_id, title, _clean(preconditions), _clean(steps)


def _collect_tests() -> list[dict]:
    rows = []
    for py_file in sorted(TESTS_DIR.glob("test_*.py")):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        # module-level marks (e.g. pytestmark = [pytest.mark.smoke])
        module_marks: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # class-level marks from decorators
                class_marks = []
                for dec in node.decorator_list:
                    class_marks.extend(_marks_from_decorator(dec))

                for item in node.body:
                    if not isinstance(item, ast.FunctionDef):
                        continue
                    if not item.name.startswith("test_"):
                        continue

                    method_marks = list(class_marks)
                    for dec in item.decorator_list:
                        method_marks.extend(_marks_from_decorator(dec))

                    raw_doc = ast.get_docstring(item) or ""
                    uc_id, title, preconditions, steps = _parse_docstring(raw_doc)

                    rows.append({
                        "file":          py_file.name,
                        "class":         node.name,
                        "method":        item.name,
                        "uc_id":         uc_id,
                        "title":         title,
                        "preconditions": preconditions,
                        "steps":         steps,
                        "marks":         ", ".join(sorted(set(method_marks))),
                    })

        # also collect module-level test functions (e.g. test_pingpong_e2e.py)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                method_marks = list(module_marks)
                for dec in node.decorator_list:
                    method_marks.extend(_marks_from_decorator(dec))
                raw_doc = ast.get_docstring(node) or ""
                uc_id, title, preconditions, steps = _parse_docstring(raw_doc)
                rows.append({
                    "file":          py_file.name,
                    "class":         "(module)",
                    "method":        node.name,
                    "uc_id":         uc_id,
                    "title":         title,
                    "preconditions": preconditions,
                    "steps":         steps,
                    "marks":         ", ".join(sorted(set(method_marks))),
                })

    return rows


# ── build workbook ────────────────────────────────────────────────────────────

def _build_workbook(rows: list[dict]) -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    headers = ["#", "File", "Class", "Test Method", "Use Case ID",
               "Title / Description", "Pre-conditions", "Steps", "Marks"]
    col_widths = [5, 26, 28, 42, 14, 46, 34, 46, 22]

    # ── freeze pane + header row ──────────────────────────────────────────────
    ws.freeze_panes = "A2"
    for c_idx, (hdr, width) in enumerate(zip(headers, col_widths), start=1):
        cell = ws.cell(row=1, column=c_idx, value=hdr)
        cell.font      = HEADER_FONT
        cell.fill      = HEADER_FILL
        cell.alignment = CTR
        cell.border    = THIN_BORDER
        ws.column_dimensions[get_column_letter(c_idx)].width = width

    ws.row_dimensions[1].height = 22

    # ── group rows by file (for colour banding by file group) ─────────────────
    file_colours: dict[str, str] = {}
    palette = ["DDEEFF", "E8F5E9", "FFF3E0", "FCE4EC", "F3E5F5",
               "E0F2F1", "FFF9C4", "E8EAF6", "F1F8E9", "E0F7FA"]

    def _file_fill(fname: str) -> PatternFill:
        if fname not in file_colours:
            idx = len(file_colours) % len(palette)
            file_colours[fname] = palette[idx]
        return PatternFill("solid", fgColor=file_colours[fname])

    # ── write data rows ───────────────────────────────────────────────────────
    for r_idx, row in enumerate(rows, start=2):
        fill = _file_fill(row["file"])
        values = [
            r_idx - 1,
            row["file"],
            row["class"],
            row["method"],
            row["uc_id"],
            row["title"],
            row["preconditions"],
            row["steps"],
            row["marks"],
        ]
        for c_idx, val in enumerate(values, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.fill      = fill
            cell.font      = BODY_FONT
            cell.alignment = WRAP
            cell.border    = THIN_BORDER

        # bold the row number
        ws.cell(row=r_idx, column=1).font = Font(bold=True, size=9, name="Calibri")
        ws.row_dimensions[r_idx].height = max(
            15,
            15 * max(
                1,
                len(str(row["steps"]).splitlines()),
                len(str(row["preconditions"]).splitlines()),
            ),
        )

    # ── auto-filter ───────────────────────────────────────────────────────────
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    # ── summary sheet ─────────────────────────────────────────────────────────
    ws_sum = wb.create_sheet("Summary")
    ws_sum.column_dimensions["A"].width = 32
    ws_sum.column_dimensions["B"].width = 14

    sum_headers = ["File", "Test Count"]
    for c_idx, hdr in enumerate(sum_headers, start=1):
        cell = ws_sum.cell(row=1, column=c_idx, value=hdr)
        cell.font      = HEADER_FONT
        cell.fill      = HEADER_FILL
        cell.alignment = CTR
        cell.border    = THIN_BORDER

    from collections import Counter
    counts = Counter(r["file"] for r in rows)
    for r_idx, (fname, cnt) in enumerate(sorted(counts.items()), start=2):
        ws_sum.cell(row=r_idx, column=1, value=fname).border = THIN_BORDER
        ws_sum.cell(row=r_idx, column=2, value=cnt).border   = THIN_BORDER
        ws_sum.cell(row=r_idx, column=2).alignment = CTR

    total_row = len(counts) + 2
    total_cell = ws_sum.cell(row=total_row, column=1, value="TOTAL")
    total_cell.font   = Font(bold=True, size=9, name="Calibri")
    total_cell.border = THIN_BORDER
    count_cell = ws_sum.cell(row=total_row, column=2, value=len(rows))
    count_cell.font      = Font(bold=True, size=9, name="Calibri")
    count_cell.alignment = CTR
    count_cell.border    = THIN_BORDER

    return wb


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("Collecting tests …")
    rows = _collect_tests()
    print(f"Found {len(rows)} test cases across {len(set(r['file'] for r in rows))} files.")

    wb = _build_workbook(rows)
    wb.save(OUT_PATH)
    print(f"Saved → {OUT_PATH}")


if __name__ == "__main__":
    main()
