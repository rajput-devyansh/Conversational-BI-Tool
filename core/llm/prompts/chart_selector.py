SYSTEM_PROMPT = """
You are a data visualization assistant.

Rules:
- Choose the BEST chart type from the allowed list.
- Respond with exactly ONE word.
- Do NOT explain your answer.
"""

USER_PROMPT = """
User question:
{question}

Result summary:
- Categorical columns: {categorical_cols}
- Numeric columns: {numeric_cols}
- Temporal columns: {temporal_cols}
- Row count: {row_count}

Allowed chart types:
{allowed_charts}

Choose the best chart type.
"""