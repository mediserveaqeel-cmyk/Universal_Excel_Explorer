# Universal Data Extractor

Developed by **Muhammad Aqeel**

A Streamlit dashboard: upload any Excel/CSV report, pick exactly the
columns you want, filter down to the rows that matter, strip out empty
rows, and download a clean extract as Excel or CSV.

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## How it works

1. **Upload** an .xlsx, .xls, or .csv file. If it's a multi-sheet
   workbook, pick the sheet. Header row is auto-detected even if there
   are title rows, logos, or blank rows above the real headers.
2. **Choose columns** (step 1) — search by name, or browse by type
   (Text / Numeric / Date) in tabs. Nothing is pre-checked; you pick
   exactly what you want, one checkbox per row.
3. **Filter rows** (step 2) — pick a column. Text columns show a
   searchable checklist of the column's real values (Excel-style
   AutoFilter) with a live "X rows will match" count. Numeric/date
   columns use condition + value (=, between, before/after, etc).
   Add as many filters as you like; they combine with AND.
4. **Remove empty rows** (step 4) — once you've picked columns, you
   can drop rows that are blank (and optionally treat 0 as blank too)
   across every column you selected, so a filtered export isn't full
   of all-zero rows.
5. **Download** the result as `.xlsx` or `.csv`.

A live stats strip (rows loaded, columns detected, columns selected,
rows in export) updates as you work.

### Mobile notes
- If opened inside an app's built-in browser (Instagram, Facebook,
  WhatsApp, etc.), the app detects it and shows a banner telling you to
  tap **⋮ → Open in Browser** — those in-app browsers block native file
  uploads.
- File type is validated after upload rather than restricted at the
  picker level, since some mobile file pickers hide Excel files when a
  strict `accept` filter is set.

## Project structure

```
app.py                       # Streamlit UI + styling
core/
  __init__.py
  loader.py                  # reads xlsx/csv, auto-detects header row
  header_detector.py         # header row detection heuristic
  filters.py                 # column type detection + row filter engine
requirements.txt
```
