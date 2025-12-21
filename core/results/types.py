from enum import Enum

class ResultType(Enum):
    EMPTY = "empty"
    METRIC = "metric"
    TIME_SERIES = "time_series"
    CATEGORICAL = "categorical"
    TABULAR = "tabular"