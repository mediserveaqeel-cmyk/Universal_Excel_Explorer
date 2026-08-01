# Universal Data Extractor

A Streamlit app: upload any Excel/CSV report, pick exactly the columns you
want by their headers, filter rows, and download the result as a new
Excel or CSV file.

## What was fixed / added

- `core/header_detector.py` was **missing** from the original files —
  `loader.py` imports it to auto-detect which row is the real header
  (handles files with title rows, logos, or blank rows above the data).
  It's now included.
- Reorganized the three original files into the `core/` package that
  `app.py`'s imports (`from core.loader import ...`) expect.
- Verified end-to-end: header detection, column selection, row filtering,
  and both download formats all tested and working.

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## How it works

1. **Upload** an .xlsx, .xls, or .csv file. If it's a multi-sheet workbook,
   pick the sheet.
2. **Choose columns** — a multiselect populated straight from the file's
   column headers. Everything is selected by default; remove what you
   don't want.
3. **Build row filters** (optional) — pick a column, an operator
   (adapts to text / numeric / date columns), and a value. Add as many
   filters as you like; they combine with AND. Remove individual filters
   or clear them all.
4. **Download** the resulting subset as `.xlsx` or `.csv`.

## Project structure

```
app.py                    # Streamlit UI
core/
  __init__.py
  loader.py                # reads xlsx/csv, auto-detects header row
  header_detector.py        # header row detection heuristic
  filters.py                # column type detection + row filter engine
requirements.txt
```
