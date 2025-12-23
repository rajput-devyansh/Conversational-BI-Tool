import pandas as pd
from core.llm.chart_selector import select_chart_type
from core.results.classifier import build_result_profile

class FakeLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, prompt):
        return self.response

ELIGIBLE = {"bar", "table", "line"}

def test_accepts_valid_chart_type():
    df = pd.DataFrame({
        "category": ["A", "B"],
        "value": [10, 20],
    })

    profile = build_result_profile(df)
    llm = FakeLLM("bar")

    chart = select_chart_type(
        llm=llm,
        question="Top categories",
        profile=profile,
        eligible_charts=ELIGIBLE,
    )

    assert chart == "bar"

def test_normalizes_chart_output():
    df = pd.DataFrame({
        "category": ["A", "B"],
        "value": [10, 20],
    })

    profile = build_result_profile(df)
    llm = FakeLLM(" Bar ")

    chart = select_chart_type(
        llm=llm,
        question="Top categories",
        profile=profile,
        eligible_charts=ELIGIBLE,
    )

    assert chart == "bar"

def test_rejects_invalid_chart_type():
    df = pd.DataFrame({
        "category": ["A", "B"],
        "value": [10, 20],
    })

    profile = build_result_profile(df)
    llm = FakeLLM("scatter")

    chart = select_chart_type(
        llm=llm,
        question="Top categories",
        profile=profile,
        eligible_charts=ELIGIBLE,
    )

    assert chart is None

def test_handles_empty_dataframe():
    df = pd.DataFrame()

    profile = build_result_profile(df)
    llm = FakeLLM("bar")

    chart = select_chart_type(
        llm=llm,
        question="Anything",
        profile=profile,
        eligible_charts=ELIGIBLE,
    )

    assert chart is None