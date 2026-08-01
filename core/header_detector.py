"""
Auto-detects which row in a messy Excel sheet is the real header row.

Many real-world exports have a few title/logo/blank rows above the actual
column headers (e.g. "Sales Report - Q1 2026" on row 0, blank row 1,
real headers on row 2). This scans the first several rows of the sheet
and picks the one that looks most like a header: mostly text, mostly
unique, and mostly non-empty, sitting just above rows that look like data.
"""

import pandas as pd

MAX_ROWS_TO_SCAN = 15


def _score_row(row_values):
    """Higher score = more header-like."""
    values = [v for v in row_values if v is not None and str(v).strip() != "" and str(v).lower() != "nan"]
    n = len(row_values)
    if n == 0 or len(values) == 0:
        return -1

    filled_ratio = len(values) / n

    str_values = [str(v).strip() for v in values]
    unique_ratio = len(set(str_values)) / len(str_values)

    # Header cells are usually text, not numbers
    numeric_count = sum(1 for v in values if _is_numeric(v))
    text_ratio = 1 - (numeric_count / len(values))

    return filled_ratio * 1.0 + unique_ratio * 1.0 + text_ratio * 1.0


def _is_numeric(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def detect_header(file, sheet_name=0):
    """
    Reads the first MAX_ROWS_TO_SCAN rows (no header assumed) and returns
    the 0-based index of the row most likely to be the real header.
    Falls back to 0 if the sheet is too small or nothing scores well.
    """
    if hasattr(file, "seek"):
        file.seek(0)

    preview = pd.read_excel(
        file, sheet_name=sheet_name, header=None, nrows=MAX_ROWS_TO_SCAN
    )

    if preview.empty:
        return 0

    best_row = 0
    best_score = -1
    for i in range(len(preview)):
        row_values = preview.iloc[i].tolist()
        score = _score_row(row_values)
        if score > best_score:
            best_score = score
            best_row = i

    return best_row
