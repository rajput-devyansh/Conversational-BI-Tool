from core.llm.prompts.chart_selector import SYSTEM_PROMPT, USER_PROMPT

def select_chart_type(llm, question: str, profile, eligible_charts: list[str]):
    if not eligible_charts:
        return None

    prompt = SYSTEM_PROMPT + USER_PROMPT.format(
        question=question,
        categorical_cols=", ".join(profile.categorical_cols) or "none",
        numeric_cols=", ".join(profile.numeric_cols) or "none",
        temporal_cols=", ".join(profile.temporal_cols) or "none",
        row_count=profile.row_count,
        allowed_charts=", ".join(eligible_charts),
    )

    try:
        response = llm.invoke(prompt)
    except Exception:
        return None

    text = response.content if hasattr(response, "content") else str(response)
    choice = text.strip().lower()

    if choice not in eligible_charts:
        return None

    return choice