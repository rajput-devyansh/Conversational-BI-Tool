from core.llm.prompts.executive_summary import SYSTEM_PROMPT, USER_PROMPT


def generate_executive_summary(
    llm,
    facts_payload: dict,
) -> str | None:
    """
    Generate a short executive summary from extracted facts.
    Returns None if generation fails.
    """

    facts_list = facts_payload.get("facts", [])
    if not facts_list:
        return None

    prompt = SYSTEM_PROMPT + USER_PROMPT.format(
        question=facts_payload.get("question", ""),
        result_type=facts_payload.get("result_type", ""),
        facts="\n".join(f"- {f}" for f in facts_list),
    )

    try:
        response = llm.invoke(prompt)
    except Exception:
        return None

    # ---- Extract text safely ----
    if hasattr(response, "content"):
        text = response.content
    else:
        text = str(response)

    # ---- Post-process hard limits ----
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Enforce 2–4 lines max
    cleaned = lines[:4]

    if not cleaned:
        return None

    return "\n".join(cleaned)