# core/suggestions/followups.py

from core.results.types import ResultType


def suggest_followups(question: str, profile) -> list[str]:
    """
    Rule-based fallback follow-up suggestions.
    """

    suggestions = []
    q = question.lower()

    if profile.result_type == ResultType.METRIC:
        if "revenue" in q:
            suggestions.extend([
                "Revenue by month",
                "Top product categories by revenue",
                "Revenue by state",
            ])

    elif profile.result_type == ResultType.TIME_SERIES:
        suggestions.extend([
            "Which month had the highest value?",
            "Top product categories by revenue",
            "Compare last 3 months",
        ])

    elif profile.result_type == ResultType.CATEGORICAL:
        suggestions.extend([
            "Revenue by month",
            "How much do the top categories contribute?",
            "Which category performs best over time?",
        ])

    if not suggestions:
        suggestions = [
            "What is the total revenue?",
            "How many orders are there?",
        ]

    return suggestions[:4]