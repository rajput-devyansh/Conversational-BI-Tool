from core.results.types import ResultType


def suggest_followups(question: str, profile) -> list[str]:
    """
    Generate rule-based follow-up questions based on
    the last question and result profile.
    """

    suggestions = []

    q = question.lower()

    # ---- Revenue metric ----
    if profile.result_type == ResultType.METRIC:
        if "revenue" in q:
            suggestions.extend([
                "Revenue by month",
                "Top product categories by revenue",
                "Revenue by state",
            ])

    # ---- Time series ----
    elif profile.result_type == ResultType.TIME_SERIES:
        suggestions.extend([
            "Top product categories by revenue",
            "Which month had the highest revenue?",
            "Compare revenue for the last 3 months",
        ])

    # ---- Categorical ----
    elif profile.result_type == ResultType.CATEGORICAL:
        suggestions.extend([
            "Revenue by month",
            "How much do the top 5 categories contribute?",
            "Which category performs best over time?",
        ])

    # ---- Fallback ----
    if not suggestions:
        suggestions.extend([
            "What is the total revenue?",
            "How many orders are there?",
        ])

    # Remove duplicates, limit to 4
    return list(dict.fromkeys(suggestions))[:4]