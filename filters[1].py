"""
Generic, column-agnostic filtering so this works on ANY sales-style
Excel file the user uploads, not just one fixed layout.
"""

import pandas as pd


def text_search(df, column, query):
    """Case-insensitive partial match on a text column."""
    if not query:
        return df
    return df[df[column].astype(str).str.contains(query, case=False, na=False)]


def date_range_filter(df, column, start_date, end_date):
    if column not in df.columns:
        return df
    dates = pd.to_datetime(df[column], errors="coerce")
    mask = pd.Series(True, index=df.index)
    if start_date:
        mask &= dates >= pd.to_datetime(start_date)
    if end_date:
        mask &= dates <= pd.to_datetime(end_date)
    return df[mask]


def value_filter(df, column, selected_values):
    """Multi-select filter, e.g. product name, region, status."""
    if not selected_values:
        return df
    return df[df[column].isin(selected_values)]


def numeric_range_filter(df, column, min_val, max_val):
    if column not in df.columns:
        return df
    nums = pd.to_numeric(df[column], errors="coerce")
    mask = pd.Series(True, index=df.index)
    if min_val is not None:
        mask &= nums >= min_val
    if max_val is not None:
        mask &= nums <= max_val
    return df[mask]
