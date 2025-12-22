import pandas as pd
import re
from core.results.types import ResultType
from core.results.profile import ResultProfile

# ---- Semantic time configuration ----

SEMANTIC_TIME_NAMES = {"date", "day", "month", "year", "week"}

DATE_PATTERNS = [
    re.compile(r"^\d{4}$"),              # YYYY
    re.compile(r"^\d{4}-\d{2}$"),         # YYYY-MM
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),   # YYYY-MM-DD
]

def looks_like_date(series: pd.Series) -> bool:
    """
    Check whether a string series looks like a date.
    Uses sampling to avoid expensive full scans.
    """
    values = series.dropna().astype(str)
    if values.empty:
        return False

    sample = values[:20]
    matches = sum(
        any(pattern.match(v) for pattern in DATE_PATTERNS)
        for v in sample
    )

    return matches / len(sample) >= 0.8


# ---- Main profile builder ----

def build_result_profile(df: pd.DataFrame) -> ResultProfile:
    """
    Build a ResultProfile by inspecting column semantics and dtypes.
    This is the single source of truth for result classification.
    """

    if df is None or df.empty:
        return ResultProfile(
            result_type=ResultType.EMPTY,
            categorical_cols=[],
            numeric_cols=[],
            temporal_cols=[],
            row_count=0,
        )

    categorical_cols = []
    numeric_cols = []
    temporal_cols = []

    for col in df.columns:
        series = df[col]
        col_name = col.lower()

        # ---- Native datetime ----
        if pd.api.types.is_datetime64_any_dtype(series):
            temporal_cols.append(col)
            continue

        # ---- Semantic datetime (e.g., "month" = "2017-01") ----
        if col_name in SEMANTIC_TIME_NAMES and looks_like_date(series):
            parsed = pd.to_datetime(series, errors="coerce")
            if parsed.notna().mean() >= 0.8:
                df[col] = parsed
            temporal_cols.append(col)
            continue

        # ---- Numeric ----
        if pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
            continue

        # ---- Categorical fallback ----
        categorical_cols.append(col)

    # ---- Result type inference (derived from profile) ----
    if len(df) == 1 and len(df.columns) == 1:
        result_type = ResultType.METRIC

    elif temporal_cols and numeric_cols:
        result_type = ResultType.TIME_SERIES

    elif categorical_cols and numeric_cols:
        result_type = ResultType.CATEGORICAL

    else:
        result_type = ResultType.TABULAR

    return ResultProfile(
        result_type=result_type,
        categorical_cols=categorical_cols,
        numeric_cols=numeric_cols,
        temporal_cols=temporal_cols,
        row_count=len(df),
    )


# ---- Backward-compatible classifier ----

def classify_result(df: pd.DataFrame) -> ResultType:
    """
    Return only the ResultType.
    Delegates to build_result_profile to avoid duplicated logic.
    """
    profile = build_result_profile(df)
    return profile.result_type