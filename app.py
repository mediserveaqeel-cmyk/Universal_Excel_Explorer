import io
import pandas as pd
import streamlit as st

from core.loader import DataLoader
from core.filters import detect_column_type, apply_rules, NUMERIC_OPS, DATE_OPS

st.set_page_config(page_title="Universal Data Extractor", page_icon="📊", layout="wide")

# ============================================================
#  THEME  --  dark navy / teal "data ops" dashboard
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {
        --bg-primary:   #0B1220;
        --bg-secondary: #101a30;
        --surface:      #16213b;
        --border:       #263353;
        --text-primary: #EDEFF5;
        --text-muted:   #93A0BC;
        --teal:         #2DD4BF;
        --teal-dim:     rgba(45, 212, 191, 0.14);
        --amber:        #F5A623;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #10233a 0%, var(--bg-primary) 45%) fixed;
        color: var(--text-primary);
    }

    /* ---------- Hero ---------- */
    .aqx-hero {
        background: linear-gradient(135deg, #0B1220 0%, #132038 55%, #0E2A2C 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.75rem;
        position: relative;
        overflow: hidden;
    }
    .aqx-hero::after {
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(45,212,191,0.18) 0%, transparent 70%);
    }
    .aqx-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--teal);
        margin-bottom: 0.5rem;
    }
    .aqx-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.1rem;
        color: var(--text-primary);
        margin: 0 0 0.35rem 0;
        line-height: 1.15;
    }
    .aqx-subtitle {
        color: var(--text-muted);
        font-size: 0.98rem;
        max-width: 640px;
        margin-bottom: 0.9rem;
    }
    .aqx-credit {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        color: var(--teal);
        background: var(--teal-dim);
        border: 1px solid rgba(45, 212, 191, 0.35);
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
    }

    /* ---------- Stat tiles ---------- */
    .aqx-stat {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: left;
    }
    .aqx-stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.3rem;
    }
    .aqx-stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--teal);
    }

    /* ---------- Step headers ---------- */
    .aqx-step {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 1.9rem 0 0.9rem 0;
    }
    .aqx-step-badge {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
        color: #06231F;
        background: var(--teal);
        width: 30px; height: 30px;
        min-width: 30px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
    }
    .aqx-step-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        color: var(--text-primary);
    }

    /* ---------- Widgets ---------- */
    .stButton>button {
        background: var(--surface);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        border-color: var(--teal);
        color: var(--teal);
    }
    .stDownloadButton>button {
        background: var(--teal);
        color: #06231F;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton>button:hover {
        background: #4EEBD8;
    }
    div[data-testid="stExpander"], div[data-testid="stForm"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }

    /* ---------- Footer ---------- */
    .aqx-footer {
        margin-top: 3rem;
        padding-top: 1.1rem;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .aqx-footer span { color: var(--teal); }

    /* ---------- Mobile responsiveness ---------- */
    @media (max-width: 480px) {
        .aqx-hero { padding: 1.25rem 1.1rem; border-radius: 12px; }
        .aqx-title { font-size: 1.5rem; }
        .aqx-subtitle { font-size: 0.88rem; }
        .aqx-step-title { font-size: 1.02rem; }
        .aqx-stat { padding: 0.7rem 0.8rem; }
        .aqx-stat-value { font-size: 1.25rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def step_header(number, title):
    st.markdown(
        f"""
        <div class="aqx-step">
            <div class="aqx-step-badge">{number}</div>
            <div class="aqx-step-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_tile(col, label, value):
    col.markdown(
        f"""
        <div class="aqx-stat">
            <div class="aqx-stat-label">{label}</div>
            <div class="aqx-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
#  HERO
# ============================================================
st.markdown(
    """
    <div class="aqx-hero">
        <div class="aqx-eyebrow">DATA EXTRACTION TOOLKIT</div>
        <div class="aqx-title">📊 Universal Data Extractor</div>
        <div class="aqx-subtitle">
            Upload any Excel or CSV report, pick exactly the columns you want,
            filter down to the rows that matter, strip out the empty noise,
            and download a clean extract.
        </div>
        <div class="aqx-credit">⚙ Developed by Muhammad Aqeel</div>
    </div>
    """,
    unsafe_allow_html=True,
)

loader = DataLoader()

# ---------------- IN-APP BROWSER WARNING ----------------
# Instagram / Facebook / WhatsApp / Line etc. open links in a restricted
# in-app WebView that blocks native file uploads -- Streamlit's uploader
# throws an error there even though the app itself is fine. Detect the
# common signatures and tell people to open in a real browser instead.
try:
    _user_agent = st.context.headers.get("User-Agent", "") or ""
except Exception:
    _user_agent = ""

_in_app_signatures = ["Instagram", "FBAN", "FBAV", "FB_IAB", "Line/", "MicroMessenger", "TikTok", "Snapchat"]
_is_in_app_browser = any(sig.lower() in _user_agent.lower() for sig in _in_app_signatures)

if _is_in_app_browser:
    st.warning(
        "⚠️ **You're viewing this inside an app's built-in browser** "
        "(Instagram, Facebook, WhatsApp, or similar). These block file uploads. "
        "Tap the **⋮** or **•••** menu at the top of the screen and choose "
        "**'Open in Browser'** (Chrome/Safari) to upload your file.",
        icon="⚠️",
    )

if "rules" not in st.session_state:
    st.session_state.rules = []  # list of dicts: {column, type, op, value}

uploaded_file = st.file_uploader(
    "Upload file",
    type=None,  # no restriction here -- some mobile browsers filter out
                # Excel files entirely when a type/accept list is set,
                # because they match by MIME type instead of extension.
                # We validate the extension ourselves below instead.
    help="Excel (.xlsx / .xls) or CSV",
)

if uploaded_file is not None:
    _valid_extensions = (".xlsx", ".xls", ".csv")
    if not uploaded_file.name.lower().endswith(_valid_extensions):
        st.error(
            f"'{uploaded_file.name}' isn't a supported file type. "
            "Please upload an .xlsx, .xls, or .csv file."
        )
        uploaded_file = None

if uploaded_file:
    sheet_names = loader.sheet_names(uploaded_file)
    sheet = sheet_names[0]
    if len(sheet_names) > 1:
        sheet = st.selectbox("Sheet", sheet_names)

    df = loader.load(uploaded_file, sheet_name=sheet)
    col_types = {c: detect_column_type(df[c]) for c in df.columns}

    with st.expander("Preview raw data"):
        st.dataframe(df.head(20), width="stretch")

    # ---------------- COLUMN SELECTION ----------------
    step_header(1, "Choose columns to extract")

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
    step_header(2, "Filter rows")

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
    step_header(3, "Select columns & filter result")

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
    step_header(4, "Remove empty rows")

    if not selected_columns:
        # Nothing selected yet in step 1 -- skip this entirely rather than
        # scanning every column in the file on every rerun. That eager
        # full-width scan was slow on wide files and, on flaky mobile
        # connections, could be slow enough to trip a proxy timeout.
        st.caption("Select at least one column in step 1 to enable empty-row cleanup.")
        drop_empty = False
    else:
        check_cols = selected_columns

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

        if drop_empty:
            sub = extracted[check_cols]

            # Vectorized emptiness check (fast even on very wide files) --
            # no per-cell Python function calls.
            na_mask = sub.isna()

            text_cols = sub.select_dtypes(include=["object", "string"]).columns
            if len(text_cols):
                blank_mask = sub[text_cols].astype(str).apply(lambda s: s.str.strip() == "")
                blank_mask = blank_mask.reindex(columns=sub.columns, fill_value=False)
            else:
                blank_mask = pd.DataFrame(False, index=sub.index, columns=sub.columns)

            if treat_zero_as_empty:
                num_cols = sub.select_dtypes(include="number").columns
                if len(num_cols):
                    zero_mask = sub[num_cols] == 0
                    zero_mask = zero_mask.reindex(columns=sub.columns, fill_value=False)
                else:
                    zero_mask = pd.DataFrame(False, index=sub.index, columns=sub.columns)
            else:
                zero_mask = pd.DataFrame(False, index=sub.index, columns=sub.columns)

            row_all_empty = (na_mask | blank_mask | zero_mask).all(axis=1)

            before = len(extracted)
            extracted = extracted[~row_all_empty]
            removed = before - len(extracted)
            st.caption(f"🧹 Removed **{removed}** empty row(s) -- **{len(extracted)}** row(s) remain.")
        else:
            st.caption(f"{len(extracted)} row(s) -- empty-row removal is off.")

    # ---------------- LIVE STATS STRIP ----------------
    s1, s2, s3, s4 = st.columns(4)
    stat_tile(s1, "Rows Loaded", f"{df.shape[0]:,}")
    stat_tile(s2, "Columns Detected", f"{df.shape[1]:,}")
    stat_tile(s3, "Columns Selected", f"{len(selected_columns):,}")
    stat_tile(s4, "Rows in Export", f"{len(extracted):,}")

    st.write("")
    st.write(f"**{len(extracted)} rows × {len(extracted.columns)} columns**")
    st.dataframe(extracted, width="stretch")

    # ---------------- DOWNLOAD ----------------
    step_header(5, "Download")
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

# ============================================================
#  FOOTER
# ============================================================
st.markdown(
    """
    <div class="aqx-footer">
        Universal Data Extractor &nbsp;•&nbsp; Developed by <span>Muhammad Aqeel</span>
    </div>
    """,
    unsafe_allow_html=True,
)
