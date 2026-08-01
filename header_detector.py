"""
Detects which row in a messy Excel sheet is the real header row.

Sales-report exports (like yours) often have title rows, blank rows,
or merged banner cells above the actual column headers. This scans
the first N rows and scores each one by how "header-like" it looks:
lots of non-empty cells, and lots of *unique* values (real headers
rarely repeat the same text across columns; data rows often do).
"""

import pandas as pd


def detect_header(file_path, sheet_name=0, max_scan_rows=20):
    preview = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        nrows=max_scan_rows,
    )

    best_row = 0
    best_score = -1

    for i in range(len(preview)):
        row = preview.iloc[i]          # <-- square brackets, not parentheses
        non_empty = row.notna().sum()
        unique = row.nunique()
        score = non_empty + unique

        if score > best_score:
            best_score = score
            best_row = i

    return best_row
