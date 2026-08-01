import io
import pandas as pd
import streamlit as st

from core.loader import DataLoader
from core.filters import text_search, value_filter, date_range_filter, numeric_range_filter

st.set_page_config(page_title="Universal Excel Explorer", layout="wide")
st.title("📊 Universal Excel Explorer")
st.caption("Upload any sales-report style Excel file, search/filter it, and download the result.")

loader = DataLoader()

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    # let the user pick a sheet if the workbook has more than one
    sheet_names = loader.sheet_names(uploaded_file)
    sheet = sheet_names[0]
    if len(sheet_names) > 1:
        sheet = st.selectbox("Sheet", sheet_names)

    df = loader.load(uploaded_file, sheet_name=sheet)

    st.success(f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")
    with st.expander("Preview raw data"):
        st.dataframe(df.head(20), use_container_width=True)

    st.sidebar.header("🔍 Search & Filter")
    filtered = df.copy()

    # --- free text search on any chosen column ---
    text_col = st.sidebar.selectbox("Search column", ["(none)"] + list(df.columns))
    if text_col != "(none)":
        query = st.sidebar.text_input(f"Search '{text_col}' contains")
        filtered = text_search(filtered, text_col, query)

    # --- multi-select filter on a categorical column ---
    cat_col = st.sidebar.selectbox("Filter column (pick values)", ["(none)"] + list(df.columns))
    if cat_col != "(none)":
        options = sorted(df[cat_col].dropna().astype(str).unique().tolist())
        chosen = st.sidebar.multiselect(f"Values in '{cat_col}'", options)
        filtered = value_filter(filtered, cat_col, chosen)

    # --- date range filter, only shown if a date-like column exists ---
    date_candidates = [c for c in df.columns if "date" in c.lower()]
    if date_candidates:
        date_col = st.sidebar.selectbox("Date column", ["(none)"] + date_candidates)
        if date_col != "(none)":
            c1, c2 = st.sidebar.columns(2)
            start = c1.date_input("From", value=None)
            end = c2.date_input("To", value=None)
            filtered = date_range_filter(filtered, date_col, start, end)

    # --- numeric range filter, only shown if a numeric column exists ---
    numeric_candidates = [c for c in df.columns if pd.to_numeric(df[c], errors="coerce").notna().any()]
    if numeric_candidates:
        num_col = st.sidebar.selectbox("Numeric column", ["(none)"] + numeric_candidates)
        if num_col != "(none)":
            n1, n2 = st.sidebar.columns(2)
            min_v = n1.number_input("Min", value=None, step=1.0)
            max_v = n2.number_input("Max", value=None, step=1.0)
            filtered = numeric_range_filter(filtered, num_col, min_v, max_v)

    st.subheader(f"Results ({len(filtered)} rows)")
    st.dataframe(filtered, use_container_width=True)

    # --- summary stats on numeric columns ---
    if numeric_candidates:
        with st.expander("Summary statistics"):
            st.dataframe(filtered[numeric_candidates].apply(pd.to_numeric, errors="coerce").describe())

    # --- download filtered result as Excel ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered.to_excel(writer, index=False, sheet_name="Filtered")
    st.download_button(
        "⬇️ Download filtered result as Excel",
        data=buffer.getvalue(),
        file_name="filtered_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Upload an Excel file to get started.")
