from core.results.profile import ResultProfile
from core.results.types import ResultType

def get_eligible_charts(profile: ResultProfile) -> list[str]:
    eligible = []

    if profile.result_type == ResultType.EMPTY:
        return eligible

    if profile.row_count == 1 and len(profile.numeric_cols) == 1:
        eligible.append("metric")

    if profile.temporal_cols:
        eligible.append("line")

    if profile.categorical_cols and profile.numeric_cols:
        eligible.append("bar")

    # Table is almost always valid
    eligible.append("table")

    # Deduplicate while preserving order
    return list(dict.fromkeys(eligible))