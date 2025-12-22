SYSTEM_PROMPT = """
You are a business intelligence assistant.

Rules:
- Respond ONLY with a JSON array of strings
- Maximum 4 questions
- Each question must be concise
- Business-focused only
- No explanations
- No SQL
- No markdown
- No numbering
"""

USER_PROMPT = """
Previous user question:
{question}

Result type:
{result_type}

Categorical columns:
{categorical_cols}

Numeric columns:
{numeric_cols}

Temporal columns:
{temporal_cols}

Row count:
{row_count}

Suggest useful follow-up business questions.
"""