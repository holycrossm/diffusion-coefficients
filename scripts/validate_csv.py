#!/usr/bin/env python3
"""Validate the living diffusion-coefficient CSV against schema.csv.

Checks (schema v1.0.0):
  - header has 113 columns, names and order match schema/schema.csv
  - record_id is unique, format DDB + 6 digits
  - schema_version is 1.0.0 on every row
  - boolean columns are true, false, or empty (missing)
  - doi is never a 2010 RiMG compilation DOI (Zhang ch. 8 / Brady ch. 20)

Exit 0 on success, 1 on any failure. Run from anywhere:
  python scripts/validate_csv.py
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "diffusion_coefficients.csv"
SCHEMA_PATH = REPO_ROOT / "schema" / "schema.csv"

EXPECTED_NCOLS = 113
SCHEMA_VERSION = "1.0.0"
RECORD_ID_RE = re.compile(r"^DDB\d{6}$")

BOOLEAN_COLUMNS = (
    "anisotropy_flag",
    "polycrystal_flag",
    "hydrous_flag",
    "direct_measurement_flag",
    "concentration_dependent_flag",
    "mixed_md_experiment_flag",
)
BOOLEAN_OK = {"true", "false", ""}

# Citation of record is the experimental paper. These two chapter DOIs are
# finding aids, never stored in the doi column (INGEST.md).
RIMG_COMPILATION_DOIS = {
    "10.2138/rmg.2010.72.8",
    "10.2138/rmg.2010.72.20",
}
RIMG_COMPILATION_RE = re.compile(
    r"10\.2138/rmg\.2010\.72\.(8|20)(?:[^\d]|$)", re.IGNORECASE
)

MAX_PRINT = 25


def load_schema(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    line = text.splitlines()[0]
    cols = next(csv.reader([line]))
    return cols


def normalize_doi(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", s, flags=re.IGNORECASE)
    s = s.strip().rstrip("/")
    return s.lower()


def main() -> int:
    errors: list[str] = []
    counts: dict[str, int] = defaultdict(int)

    if not SCHEMA_PATH.is_file():
        print(f"FAIL: missing schema {SCHEMA_PATH}", file=sys.stderr)
        return 1
    if not DATA_PATH.is_file():
        print(f"FAIL: missing data {DATA_PATH}", file=sys.stderr)
        return 1

    schema_cols = load_schema(SCHEMA_PATH)
    if len(schema_cols) != EXPECTED_NCOLS:
        errors.append(
            f"schema.csv has {len(schema_cols)} columns; expected {EXPECTED_NCOLS}"
        )

    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        sample = f.read(4)
        f.seek(0)
        if sample.startswith("\ufeff"):
            errors.append("data CSV starts with a UTF-8 BOM; save as UTF-8 without BOM")
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("FAIL: data CSV is empty", file=sys.stderr)
            return 1

        if header != schema_cols:
            if len(header) != len(schema_cols):
                errors.append(
                    f"data header has {len(header)} columns; "
                    f"schema has {len(schema_cols)} (expected {EXPECTED_NCOLS})"
                )
            mismatched = [
                i
                for i, (a, b) in enumerate(zip(header, schema_cols))
                if a != b
            ]
            extra = header[len(schema_cols) :]
            missing = schema_cols[len(header) :]
            if mismatched:
                i = mismatched[0]
                errors.append(
                    f"header mismatch at column {i}: data={header[i]!r} schema={schema_cols[i]!r}"
                )
                if len(mismatched) > 1:
                    errors.append(f"  …and {len(mismatched) - 1} further name mismatches")
            if extra:
                errors.append(f"data has extra columns: {extra[:8]}")
            if missing:
                errors.append(f"data missing columns: {missing[:8]}")
            elif set(header) == set(schema_cols) and header != schema_cols:
                errors.append("header names match schema but column order differs")

        seen_ids: dict[str, int] = {}
        n_rows = 0
        n_doi = 0

        for lineno, row in enumerate(reader, start=2):
            n_rows += 1
            if len(row) != len(schema_cols):
                counts["width"] += 1
                if counts["width"] <= MAX_PRINT:
                    errors.append(
                        f"line {lineno}: {len(row)} fields, expected {len(schema_cols)}"
                    )
                continue
            rec = dict(zip(schema_cols, row))

            rid = rec.get("record_id", "")
            if not rid:
                counts["id"] += 1
                if counts["id"] <= MAX_PRINT:
                    errors.append(f"line {lineno}: empty record_id")
            elif not RECORD_ID_RE.match(rid):
                counts["id"] += 1
                if counts["id"] <= MAX_PRINT:
                    errors.append(
                        f"line {lineno}: record_id {rid!r} is not DDB + 6 digits"
                    )
            elif rid in seen_ids:
                counts["id"] += 1
                if counts["id"] <= MAX_PRINT:
                    errors.append(
                        f"line {lineno}: duplicate record_id {rid} "
                        f"(first seen line {seen_ids[rid]})"
                    )
            else:
                seen_ids[rid] = lineno

            ver = rec.get("schema_version", "")
            if ver != SCHEMA_VERSION:
                counts["version"] += 1
                if counts["version"] <= MAX_PRINT:
                    errors.append(
                        f"line {lineno} {rid}: schema_version={ver!r}, expected {SCHEMA_VERSION}"
                    )

            for col in BOOLEAN_COLUMNS:
                val = rec.get(col, "")
                if val not in BOOLEAN_OK:
                    counts["bool"] += 1
                    if counts["bool"] <= MAX_PRINT:
                        errors.append(
                            f"line {lineno} {rid}: {col}={val!r} "
                            f"(allowed: true, false, or empty)"
                        )

            doi_raw = rec.get("doi", "")
            if doi_raw.strip():
                n_doi += 1
                doi_n = normalize_doi(doi_raw)
                banned = doi_n in RIMG_COMPILATION_DOIS or bool(
                    RIMG_COMPILATION_RE.search(doi_raw)
                )
                if banned:
                    counts["doi"] += 1
                    if counts["doi"] <= MAX_PRINT:
                        errors.append(
                            f"line {lineno} {rid}: doi {doi_raw!r} is a RiMG 72 "
                            f"compilation DOI; cite the primary experiment instead"
                        )

    for kind, n in counts.items():
        if n > MAX_PRINT:
            errors.append(f"  …{n - MAX_PRINT} more {kind} error(s) omitted")

    print(f"schema columns: {len(schema_cols)}")
    print(f"data rows:      {n_rows}")
    print(f"unique ids:     {len(seen_ids)}")
    print(f"dois filled:    {n_doi}")
    print(f"schema_version: {SCHEMA_VERSION}")

    if errors:
        print(f"\nFAIL ({len(errors)} message(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
