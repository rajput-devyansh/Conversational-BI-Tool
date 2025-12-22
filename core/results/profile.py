from dataclasses import dataclass
from typing import List
from core.results.types import ResultType


@dataclass
class ResultProfile:
    result_type: ResultType
    categorical_cols: List[str]
    numeric_cols: List[str]
    temporal_cols: List[str]
    row_count: int