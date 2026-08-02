"""
Generic, column-agnostic filtering so this works on ANY sales-style
Excel/CSV file the user uploads, not just one fixed layout.

The key piece here is apply_rules(): it takes a list of user-built
filter rules (column + operator + value) and ANDs them together,
so the extractor can filter by any combination of columns/rows.
"""

import pandas as pd

TEXT_OPS = ["contains", "equals", "not equals", "starts with", "ends with", "is one of"]
NUMERIC_OPS = ["=", "!=", ">", ">=", "<", "<=", "between"]
DATE_OPS = ["on", "before", "after", "between"]


def detect_column_type(series):
    """Guess whether a column should be treated as text, numeric, or date."""
    if pd.to_numeric(series, errors="coerce").notna().mean() > 0.8:
        return "numeric"
    if pd.to_datetime(series, errors="coerce", format="mixed").notna().mean() > 0.8:
        return "date"
    return "text"


def _apply_text_rule(df, column, op, value):
    col = df[column].astype(str)
    if op == "contains":
        return df[col.str.contains(str(value), case=False, na=False)]
    if op == "equals":
        return df[col.str.lower() == str(value).lower()]
    if op == "not equals":
        return df[col.str.lower() != str(value).lower()]
    if op == "starts with":
        return df[col.str.lower().str.startswith(str(value).lower(), na=False)]
    if op == "ends with":
        return df[col.str.lower().str.endswith(str(value).lower(), na=False)]
    if op == "is one of":
        values = [v.strip().lower() for v in value] if isinstance(value, list) else [str(value).lower()]
        return df[col.str.lower().isin(values)]
    return df


def _apply_numeric_rule(df, column, op, value):
    nums = pd.to_numeric(df[column], errors="coerce")
    if op == "between":
        lo, hi = value
        mask = pd.Series(True, index=df.index)
        if lo is not None:
            mask &= nums >= lo
        if hi is not None:
            mask &= nums <= hi
        return df[mask]
    ops = {
        "=": lambda: nums == value,
        "!=": lambda: nums != value,
        ">": lambda: nums > value,
        ">=": lambda: nums >= value,
        "<": lambda: nums < value,
        "<=": lambda: nums <= value,
    }
    return df[ops[op]()] if op in ops and value is not None else df


def _apply_date_rule(df, column, op, value):
    dates = pd.to_datetime(df[column], errors="coerce")
    if op == "between":
        start, end = value
        mask = pd.Series(True, index=df.index)
        if start:
            mask &= dates >= pd.to_datetime(start)
        if end:
            mask &= dates <= pd.to_datetime(end)
        return df[mask]
    if op == "on" and value:
        return df[dates.dt.date == pd.to_datetime(value).date()]
    if op == "before" and value:
        return df[dates < pd.to_datetime(value)]
    if op == "after" and value:
        return df[dates > pd.to_datetime(value)]
    return df


def apply_rule(df, rule):
    """rule = {'column': str, 'type': 'text'|'numeric'|'date', 'op': str, 'value': ...}"""
    column, kind, op, value = rule["column"], rule["type"], rule["op"], rule["value"]
    if kind == "text":
        return _apply_text_rule(df, column, op, value)
    if kind == "numeric":
        return _apply_numeric_rule(df, column, op, value)
    if kind == "date":
        return _apply_date_rule(df, column, op, value)
    return df


def apply_rules(df, rules):
    """Apply a list of rules with AND logic; returns the filtered DataFrame."""
    result = df
    for rule in rules:
        result = apply_rule(result, rule)
    return result
