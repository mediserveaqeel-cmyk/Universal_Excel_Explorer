import io
import pandas as pd
import streamlit as st

from core.loader import DataLoader
from core.filters import detect_column_type, apply_rules, TEXT_OPS, NUMERIC_OPS, DATE_OPS

st.set_page_config(page_title="Universal Data Extractor", layout="wide")
st.title("📊 Universal Data Extractor")
st.caption("Upload any Excel/CSV report, pick exactly the columns you want, filter the rows you want, and download the extract.")

loader = DataLoader()

if "rules" not in st.session_state:
    st.session_state.rules = []  # list of dicts: {column, type, op, value}

uploaded_file = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    sheet_names = loader.sheet_names(uploaded_file)
    sheet = sheet_names[0]
    if len(sheet_names) > 1:
        sheet = st.selectbox("Sheet", sheet_names)

    df = loader.load(uploaded_file, sheet_name=sheet)
    col_types = {c: detect_column_type(df[c]) for c in df.columns}

    st.success(f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")
    with st.expander("Preview raw data"):
        st.dataframe(df.head(20), use_container_width=True)

    # ---------------- COLUMN SELECTION ----------------
    st.subheader("1️⃣ Choose columns to extract")
    selected_columns = st.multiselect(
        "Columns to keep in the output",
        options=list(df.columns),
        default=list(df.columns),
    )

    # ---------------- ROW FILTER BUILDER ----------------
    st.subheader("2️⃣ Build row filters")

    with st.form("add_rule_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 3])

        rule_column = c1.selectbox("Column", options=list(df.columns), key="rule_col")
        kind = col_types.get(rule_column, "text")
        op_options = {"text": TEXT_OPS, "numeric": NUMERIC_OPS, "date": DATE_OPS}[kind]
        rule_op = c2.selectbox("Condition", options=op_options, key="rule_op")

        if kind == "numeric" and rule_op == "between":
            v1 = c3.number_input("Min", value=0.0, key="rule_min")
            v2 = c3.number_input("Max", value=0.0, key="rule_max")
            rule_value = (v1, v2)
        elif kind == "date" and rule_op == "between":
            v1 = c3.date_input("From", value=None, key="rule_from")
            v2 = c3.date_input("To", value=None, key="rule_to")
            rule_value = (v1, v2)
        elif kind == "date":
            rule_value = c3.date_input("Date", value=None, key="rule_date")
        elif kind == "numeric":
            rule_value = c3.number_input("Value", value=0.0, key="rule_num")
        elif rule_op == "is one of":
            options = sorted(df[rule_column].dropna().astype(str).unique().tolist())
            rule_value = c3.multiselect("Values", options, key="rule_multi")
        else:
            rule_value = c3.text_input("Value", key="rule_text")

        submitted = st.form_submit_button("➕ Add filter")
        if submitted:
            st.session_state.rules.append(
                {"column": rule_column, "type": kind, "op": rule_op, "value": rule_value}
            )

    if st.session_state.rules:
        st.write("**Active filters** (all must match):")
        for i, rule in enumerate(st.session_state.rules):
            rc1, rc2 = st.columns([6, 1])
            rc1.write(f"`{rule['column']}` {rule['op']} `{rule['value']}`")
            if rc2.button("Remove", key=f"remove_{i}"):
                st.session_state.rules.pop(i)
                st.rerun()
        if st.button("Clear all filters"):
            st.session_state.rules = []
            st.rerun()

    # ---------------- EXTRACT ----------------
    st.subheader("3️⃣ Extracted result")

    try:
        filtered = apply_rules(df, st.session_state.rules)
    except Exception as e:
        st.error(f"A filter couldn't be applied: {e}")
        filtered = df

    extracted = filtered[selected_columns] if selected_columns else filtered

    st.write(f"**{len(extracted)} rows × {len(extracted.columns)} columns**")
    st.dataframe(extracted, use_container_width=True)

    # ---------------- DOWNLOAD ----------------
    st.subheader("4️⃣ Download")
    dl_format = st.radio("Format", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True)

    if dl_format == "Excel (.xlsx)":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            extracted.to_excel(writer, index=False, sheet_name="Extracted")
        st.download_button(
            "⬇️ Download extracted data",
            data=buffer.getvalue(),
            file_name="extracted_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        csv_bytes = extracted.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download extracted data",
            data=csv_bytes,
            file_name="extracted_data.csv",
            mime="text/csv",
        )
else:
    st.info("Upload a file to get started.")
