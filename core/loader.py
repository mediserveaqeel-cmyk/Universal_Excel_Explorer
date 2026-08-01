"""
Loads an Excel file into a clean DataFrame, auto-detecting the header row.

Works with:
  - a file path (str)               -> loader.load("sales.xlsx")
  - a Streamlit UploadedFile object -> loader.load(uploaded_file)
because pd.read_excel accepts both.
"""

import pandas as pd
from core.header_detector import detect_header


class DataLoader:

    def load(self, file, sheet_name=0):
        # detect_header needs to read the file, then read_excel needs to
        # read it again from the start -> reset the pointer in between
        # (only relevant for file-like objects, harmless for paths).
        header_row = detect_header(file, sheet_name=sheet_name)
        if hasattr(file, "seek"):
            file.seek(0)

        df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)

        # drop fully-empty rows/columns that sometimes survive the header guess
        df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
        df.columns = [str(c).strip() for c in df.columns]

        return df

    def sheet_names(self, file):
        if hasattr(file, "seek"):
            file.seek(0)
        return pd.ExcelFile(file).sheet_names
