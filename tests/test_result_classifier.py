import pandas as pd
from core.results.classifier import classify_result, build_result_profile
from core.results.types import ResultType

def test_empty_dataframe():
    df = pd.DataFrame()
    assert classify_result(df) == ResultType.EMPTY

def test_single_value_metric():
    df = pd.DataFrame({"total_orders": [100]})
    assert classify_result(df) == ResultType.METRIC

def test_time_series_by_month():
    df = pd.DataFrame({
        "month": ["2024-01", "2024-02"],
        "revenue": [1000, 1200]
    })
    assert classify_result(df) == ResultType.TIME_SERIES

def test_categorical_result():
    df = pd.DataFrame({
        "category": ["electronics", "furniture"],
        "revenue": [5000, 3000]
    })
    assert classify_result(df) == ResultType.CATEGORICAL

def test_tabular_result():
    df = pd.DataFrame({
        "a": [1, 2],
        "b": [3, 4],
        "c": [5, 6],
    })
    assert classify_result(df) == ResultType.TABULAR

def test_result_profile_columns():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2024-01-01", "2024-02-01"]),
        "revenue": [100, 200]
    })

    profile = build_result_profile(df)

    assert profile.result_type == ResultType.TIME_SERIES
    assert "month" in profile.temporal_cols
    assert "revenue" in profile.numeric_cols