import io
import pandas as pd
import streamlit as st

from core.loader import DataLoader
from core.filters import detect_column_type, apply_rules, NUMERIC_OPS, DATE_OPS

st.set_page_config(page_title="Universal Data Extractor by Muhammad AQEEL", layout="wide")
st.title("📊 Universal Data Extractor by Muhammad AQEEL")
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

    # Reset the per-column checkbox state whenever a new file/sheet is loaded.
    # Nothing is pre-checked -- you choose exactly the columns you want.
    file_signature = (uploaded_file.name, sheet, tuple(df.columns))
    if st.session_state.get("col_signature") != file_signature:
        st.session_state.col_signature = file_signature
        st.session_state.col_selected = {c: False for c in df.columns}

    def _columns_by_type(kind):
        return [c for c in df.columns if col_types.get(c) == kind]

    search_term = st.text_input(
        "🔍 Search columns",
        placeholder="Type part of a column name to find it fast...",
        key="col_search",
    )

    # Global select all / clear all (applies across every tab)
    gcol1, gcol2, gcol3 = st.columns([1, 1, 6])
    if gcol1.button("✅ Select all columns"):
        for c in df.columns:
            st.session_state.col_selected[c] = True
        st.rerun()
    if gcol2.button("⬜ Clear all columns"):
        for c in df.columns:
            st.session_state.col_selected[c] = False
        st.rerun()

    if search_term:
        # While searching, ignore the type tabs and show one flat matching
        # list -- the person doesn't know (or care) which tab a column is in.
        matches = [c for c in df.columns if search_term.lower() in c.lower()]
        st.caption(f"🔍 **{len(matches)} column(s)** match '{search_term}'")

        if matches:
            mcol1, mcol2, _ = st.columns([1, 1, 6])
            if mcol1.button("Select all matches"):
                for c in matches:
                    st.session_state.col_selected[c] = True
                st.rerun()
            if mcol2.button("Clear all matches"):
                for c in matches:
                    st.session_state.col_selected[c] = False
                st.rerun()

            for c in matches:
                st.session_state.col_selected[c] = st.checkbox(
                    c,
                    value=st.session_state.col_selected.get(c, False),
                    key=f"chk_{c}",
                )
        else:
            st.caption("No columns match your search.")
    else:
        tab_defs = [
            ("🔤 Text", _columns_by_type("text")),
            ("🔢 Numeric", _columns_by_type("numeric")),
            ("📅 Date", _columns_by_type("date")),
        ]

        tabs = st.tabs([f"{label} ({len(cols)})" for label, cols in tab_defs])

        for tab, (label, cols) in zip(tabs, tab_defs):
            with tab:
                if not cols:
                    st.caption("No columns of this type.")
                    continue

                tcol1, tcol2, _ = st.columns([1, 1, 6])
                if tcol1.button("Select all in tab", key=f"select_all_{label}"):
                    for c in cols:
                        st.session_state.col_selected[c] = True
                    st.rerun()
                if tcol2.button("Clear tab", key=f"clear_all_{label}"):
                    for c in cols:
                        st.session_state.col_selected[c] = False
                    st.rerun()

                for c in cols:
                    st.session_state.col_selected[c] = st.checkbox(
                        c,
                        value=st.session_state.col_selected.get(c, False),
                        key=f"chk_{c}",
                    )

    selected_columns = [c for c in df.columns if st.session_state.col_selected.get(c)]
    st.caption(f"**{len(selected_columns)} of {len(df.columns)} columns selected**")

    # ---------------- ROW FILTER BUILDER ----------------
    st.subheader("2️⃣ Filter rows")

    filter_column = st.selectbox(
        "Which column do you want to filter by?",
        options=["-- choose a column --"] + list(df.columns),
        key="filter_col_select",
    )

    if filter_column != "-- choose a column --":
        kind = col_types.get(filter_column, "text")

        if kind == "text":
            # Excel-style filter: search the real values in this column,
            # then check off exactly the ones you want to keep.
            st.markdown(f"Pick the values to **keep** from `{filter_column}`:")

            value_search = st.text_input(
                "🔍 Search values in this column",
                key=f"val_search_{filter_column}",
            )

            all_values = sorted(df[filter_column].dropna().astype(str).unique().tolist())
            visible_values = (
                [v for v in all_values if value_search.lower() in v.lower()]
                if value_search else all_values
            )

            state_key = f"valsel_{filter_column}"
            if state_key not in st.session_state:
                st.session_state[state_key] = set()

            vb1, vb2, _ = st.columns([1, 1, 5])
            if vb1.button("Select all shown", key=f"selall_{filter_column}"):
                st.session_state[state_key].update(visible_values)
                st.rerun()
            if vb2.button("Clear all shown", key=f"clrall_{filter_column}"):
                for v in visible_values:
                    st.session_state[state_key].discard(v)
                st.rerun()

            with st.container(height=260):
                if not visible_values:
                    st.caption("No values match your search.")
                for v in visible_values:
                    checked = st.checkbox(
                        v,
                        value=v in st.session_state[state_key],
                        key=f"chkval_{filter_column}_{v}",
                    )
                    if checked:
                        st.session_state[state_key].add(v)
                    else:
                        st.session_state[state_key].discard(v)

            selected_values = sorted(st.session_state[state_key])
            matched_rows = (
                df[df[filter_column].astype(str).isin(selected_values)].shape[0]
                if selected_values else 0
            )
            st.caption(
                f"🔎 **{len(visible_values)} value(s)** shown for '{value_search}'  •  "
                f"**{len(selected_values)} checked**  •  **{matched_rows} row(s) will match**"
            )

            if st.button(f"➕ Add filter on `{filter_column}`", key=f"apply_{filter_column}"):
                if selected_values:
                    st.session_state.rules.append(
                        {"column": filter_column, "type": "text", "op": "is one of", "value": selected_values}
                    )
                    del st.session_state[state_key]
                    st.rerun()
                else:
                    st.warning("Check at least one value first.")

        else:
            # Numeric / date columns keep the condition + value approach
            op_options = NUMERIC_OPS if kind == "numeric" else DATE_OPS
            with st.form(f"add_rule_form_{filter_column}", clear_on_submit=True):
                fc1, fc2 = st.columns(2)
                rule_op = fc1.selectbox("Condition", options=op_options, key=f"rule_op_{filter_column}")

                if kind == "numeric" and rule_op == "between":
                    v1 = fc2.number_input("Min", value=0.0, key=f"rule_min_{filter_column}")
                    v2 = fc2.number_input("Max", value=0.0, key=f"rule_max_{filter_column}")
                    rule_value = (v1, v2)
                elif kind == "date" and rule_op == "between":
                    v1 = fc2.date_input("From", value=None, key=f"rule_from_{filter_column}")
                    v2 = fc2.date_input("To", value=None, key=f"rule_to_{filter_column}")
                    rule_value = (v1, v2)
                elif kind == "date":
                    rule_value = fc2.date_input("Date", value=None, key=f"rule_date_{filter_column}")
                else:
                    rule_value = fc2.number_input("Value", value=0.0, key=f"rule_num_{filter_column}")

                submitted = st.form_submit_button(f"➕ Add filter on {filter_column}")
                if submitted:
                    st.session_state.rules.append(
                        {"column": filter_column, "type": kind, "op": rule_op, "value": rule_value}
                    )
                    st.rerun()

    if st.session_state.rules:
        st.write("**Active filters** (all must match):")
        for i, rule in enumerate(st.session_state.rules):
            rc1, rc2 = st.columns([6, 1])
            if rule["op"] == "is one of" and isinstance(rule["value"], list):
                preview = ", ".join(rule["value"][:5])
                if len(rule["value"]) > 5:
                    preview += f", … (+{len(rule['value']) - 5} more)"
                rc1.write(f"`{rule['column']}` is one of: {preview}")
            else:
                rc1.write(f"`{rule['column']}` {rule['op']} `{rule['value']}`")
            if rc2.button("Remove", key=f"remove_{i}"):
                st.session_state.rules.pop(i)
                st.rerun()
        if st.button("Clear all filters"):
            st.session_state.rules = []
            st.rerun()

    # ---------------- EXTRACT ----------------
    st.subheader("3️⃣ Select columns & filter result")

    try:
        filtered = apply_rules(df, st.session_state.rules)
    except Exception as e:
        st.error(f"A filter couldn't be applied: {e}")
        filtered = df

    if selected_columns:
        extracted = filtered[selected_columns]
    else:
        extracted = filtered
        st.info("No columns checked yet in step 1 -- showing all columns. Check the ones you want to narrow this down.")

    # ---------------- CLEAN EMPTY ROWS ----------------
    st.subheader("4️⃣ Remove empty rows")

    check_cols = selected_columns if selected_columns else list(extracted.columns)

    ec1, ec2 = st.columns(2)
    drop_empty = ec1.checkbox(
        "Drop rows that are empty across all selected columns",
        value=True,
        help="A row is removed only if EVERY selected column is blank for it -- "
             "rows with at least one value stay.",
    )
    treat_zero_as_empty = ec2.checkbox(
        "Also treat 0 as empty",
        value=True,
        help="Useful for quantity/value columns where 0 means 'no data', like unsold products.",
    )

    if drop_empty and check_cols:
        sub = extracted[check_cols]

        def _cell_is_empty(v):
            if pd.isna(v):
                return True
            if isinstance(v, str) and v.strip() == "":
                return True
            if treat_zero_as_empty and isinstance(v, (int, float)) and not isinstance(v, bool) and v == 0:
                return True
            return False

        empty_mask = sub.apply(lambda col: col.map(_cell_is_empty))
        row_all_empty = empty_mask.all(axis=1)

        before = len(extracted)
        extracted = extracted[~row_all_empty]
        removed = before - len(extracted)
        st.caption(f"🧹 Removed **{removed}** empty row(s) -- **{len(extracted)}** row(s) remain.")
    else:
        st.caption(f"{len(extracted)} row(s) -- empty-row removal is off.")

    st.write(f"**{len(extracted)} rows × {len(extracted.columns)} columns**")
    st.dataframe(extracted, use_container_width=True)

    # ---------------- DOWNLOAD ----------------
    st.subheader("5️⃣ Download")
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
