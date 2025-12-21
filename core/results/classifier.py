import pandas as pd
from core.results.types import ResultType


def classify_result(df: pd.DataFrame) -> ResultType:
    """
    Inspect a DataFrame and classify the result shape.
    """

    # ---- Empty ----
    if df is None or df.empty:
        return ResultType.EMPTY

    rows, cols = df.shape

    # ---- Single-value metric ----
    if rows == 1 and cols == 1:
        return ResultType.METRIC

    column_names = [c.lower() for c in df.columns]

    # ---- Time series ----
    if "month" in column_names or "date" in column_names:
        if cols == 2:
            return ResultType.TIME_SERIES

    # ---- Categorical (e.g., top categories, sellers, states) ----
    if cols == 2:
        return ResultType.CATEGORICAL

    # ---- Default ----
    return ResultType.TABULAR