"""
Loads an Excel or CSV file into a clean DataFrame, auto-detecting the header row.

Works with:
  - a file path (str)               -> loader.load("sales.xlsx")
  - a Streamlit UploadedFile object -> loader.load(uploaded_file)
"""

import pandas as pd
from core.header_detector import detect_header


def _get_name(file):
    """Works for both file paths (str) and Streamlit UploadedFile objects."""
    return file if isinstance(file, str) else getattr(file, "name", "")


class DataLoader:

    def is_csv(self, file):
        return _get_name(file).lower().endswith(".csv")

    def load(self, file, sheet_name=0):
        if self.is_csv(file):
            if hasattr(file, "seek"):
                file.seek(0)
            df = pd.read_csv(file)
        else:
            # detect_header needs to read the file, then read_excel needs to
            # read it again from the start -> reset the pointer in between
            header_row = detect_header(file, sheet_name=sheet_name)
            if hasattr(file, "seek"):
                file.seek(0)
            df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)

        # drop fully-empty rows/columns that sometimes survive the header guess
        df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
        df.columns = [str(c).strip() for c in df.columns]

        return df

    def sheet_names(self, file):
        if self.is_csv(file):
            return ["(csv - single sheet)"]
        if hasattr(file, "seek"):
            file.seek(0)
        return pd.ExcelFile(file).sheet_names
