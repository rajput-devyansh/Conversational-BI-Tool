import json
import re
from core.llm.prompts.followups import SYSTEM_PROMPT, USER_PROMPT


def _extract_json_array(text: str) -> list[str]:
    """
    Extract the first JSON array from text safely.
    """
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []

    try:
        data = json.loads(match.group())
        if isinstance(data, list):
            return [s.strip() for s in data if isinstance(s, str) and s.strip()]
    except Exception:
        return []

    return []


def generate_followups_llm(llm, question: str, profile, max_items: int = 4) -> list[str]:
    prompt = SYSTEM_PROMPT + USER_PROMPT.format(
        question=question,
        result_type=profile.result_type.value,
        categorical_cols=", ".join(profile.categorical_cols),
        numeric_cols=", ".join(profile.numeric_cols),
        temporal_cols=", ".join(profile.temporal_cols),
        row_count=profile.row_count,
    )

    try:
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)

        suggestions = _extract_json_array(text)
        return suggestions[:max_items]

    except Exception:
        return []