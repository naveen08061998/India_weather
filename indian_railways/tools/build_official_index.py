"""
One-off importer: parses the official Ministry of Railways "Trains at a
Glance 2026" Train Name Index PDF (published on indianrailways.gov.in) into
a JSON reference list of {name, numbers, from_to_raw, table_no}.

This gives current (2026), authoritative train names/numbers/endpoints —
but NOT full intermediate-stop schedules (those live in the actual timetable
tables referenced by "table_no", which aren't parsed here). Entries from
this index are used only to validate/update names of trains we already have
full schedules for, and as a searchable reference list for trains we don't.

Source: https://indianrailways.gov.in/railwayboard/uploads/directorate/coaching/TAG_2026/Train_Name_Index.pdf

Run:
    python -m indian_railways.tools.build_official_index
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

URL = ("https://indianrailways.gov.in/railwayboard/uploads/directorate/"
       "coaching/TAG_2026/Train_Name_Index.pdf")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PDF_PATH = RAW_DIR / "Train_Name_Index.pdf"
OUT_PATH = DATA_DIR / "official_train_index_2026.json"

NUMBER_RE = re.compile(r"\d{4,5}(?:/\d{4,5})?")
HEADER_NOISE = re.compile(
    r"Train\s*Name\s*Train\s*No\s*From\s*Station\s*To\s*Station\s*Table\s*No\.?",
    re.IGNORECASE,
)
# A "Table No." value: 1-3 digit table numbers (optionally suffixed like "23A"),
# comma-separated. This always sits right after From/To and right before the
# NEXT row's train name, so the LAST such run in a chunk marks that boundary.
TABLE_NO_RUN = re.compile(r"\b\d{1,3}[A-Za-z]?(?:\s*,\s*\d{1,3}[A-Za-z]?)*\b")


def _download() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if PDF_PATH.exists():
        print(f"  Already downloaded ({PDF_PATH.stat().st_size / 1e6:.2f} MB)")
        return
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(PDF_PATH, "wb") as f:
        f.write(resp.read())
    print(f"  Downloaded {PDF_PATH.stat().st_size / 1e6:.2f} MB")


def _extract_text() -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(PDF_PATH))
    pages = [HEADER_NOISE.sub(" ", p.extract_text() or "") for p in reader.pages]
    return "\n".join(pages)


def _parse(text: str) -> list[dict]:
    matches = list(NUMBER_RE.finditer(text))
    entries = []
    # Name for row 0 is whatever precedes the first number (just the header,
    # already stripped). Each subsequent row's name is discovered while
    # parsing the PREVIOUS row's trailing chunk (see `pending_name` below).
    pending_name = re.sub(r"\s+", " ", text[:matches[0].start()]).strip(" .") if matches else ""

    for i, m in enumerate(matches):
        name = pending_name
        numbers = m.group(0).split("/")
        chunk_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.end():chunk_end]

        table_matches = list(TABLE_NO_RUN.finditer(chunk))
        if table_matches:
            last = table_matches[-1]
            from_to_raw = re.sub(r"\s+", " ", chunk[:last.start()]).strip()
            table_no = last.group(0).strip()
            pending_name = re.sub(r"\s+", " ", chunk[last.end():]).strip(" .")
        else:
            from_to_raw = re.sub(r"\s+", " ", chunk).strip()
            table_no = ""
            pending_name = ""

        if not name or len(name) > 60:
            continue  # page-break noise (empty or absurdly long "name")
        entries.append({
            "name": name,
            "numbers": numbers,
            "from_to_raw": from_to_raw,
            "table_no": table_no,
        })
    return entries


def main() -> None:
    print("Fetching official Train Name Index (Trains at a Glance 2026)...")
    _download()
    print("Extracting PDF text...")
    text = _extract_text()
    print("Parsing entries...")
    entries = _parse(text)
    print(f"  Parsed {len(entries)} entries")
    OUT_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
