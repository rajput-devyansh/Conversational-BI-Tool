import pandas as pd
from core.results.types import ResultType
from core.results.profile import ResultProfile

def extract_summary_facts(
    df: pd.DataFrame,
    profile: ResultProfile,
    question: str | None = None,
) -> dict:
    """
    Extract deterministic, business-safe facts from a result DataFrame.
    These facts are later passed to the LLM for executive summarization.
    """

    facts = {
        "question": question or "",
        "result_type": profile.result_type.value,
        "facts": [],
    }

    if df is None or df.empty:
        return facts

    # ---------------- TIME SERIES ----------------
    if profile.result_type == ResultType.TIME_SERIES:
        time_col = profile.temporal_cols[0]
        value_col = profile.numeric_cols[0]

        series = df[[time_col, value_col]].dropna()

        if len(series) < 2:
            return facts

        first_time = series.iloc[0][time_col]
        last_time = series.iloc[-1][time_col]

        first_value = series.iloc[0][value_col]
        last_value = series.iloc[-1][value_col]

        # Trend detection
        if last_value > first_value:
            trend = "increasing"
        elif last_value < first_value:
            trend = "decreasing"
        else:
            trend = "stable"

        peak_value = series[value_col].max()

        facts["facts"].extend([
            f"The data spans from {first_time} to {last_time}.",
            f"The overall trend is {trend}.",
            f"The value starts at {round(first_value, 2)} and ends at {round(last_value, 2)}.",
            f"The highest observed value is {round(peak_value, 2)}.",
        ])

        return facts

    # ---------------- CATEGORICAL ----------------
    if profile.result_type == ResultType.CATEGORICAL:
        category_col = profile.categorical_cols[0]
        value_col = profile.numeric_cols[0]

        series = df[[category_col, value_col]].dropna()

        if series.empty:
            return facts

        top_row = series.sort_values(value_col, ascending=False).iloc[0]
        total_categories = series[category_col].nunique()

        facts["facts"].extend([
            f"The top category is {top_row[category_col]}.",
            f"It has the highest value at {round(top_row[value_col], 2)}.",
            f"There are {total_categories} categories in total.",
        ])

        return facts

    # ---------------- TABULAR ----------------
    if profile.result_type == ResultType.TABULAR:
        facts["facts"].extend([
            f"The result contains {len(df)} rows.",
            f"It includes {len(df.columns)} columns.",
        ])

        if profile.temporal_cols:
            facts["facts"].append(
                f"The data includes time-related information."
            )

        if profile.categorical_cols:
            facts["facts"].append(
                f"The data includes categorical attributes."
            )

        if profile.numeric_cols:
            facts["facts"].append(
                f"The data includes numeric measures."
            )

        return facts

    return facts