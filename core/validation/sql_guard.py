import re

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop",
    "alter", "truncate", "create",
    "attach", "detach", "pragma"
]

def validate_sql(query: str, default_limit: int = 1000) -> str:
    if not query or not isinstance(query, str):
        raise ValueError("Empty or invalid SQL query.")

    sql = query.strip()

    # ---- Strip markdown code fences if present ----
    if sql.startswith("```"):
        sql = sql.strip("`")
        sql = sql.replace("sql", "", 1).strip()

    sql_lower = sql.lower()

    # ---- Block multiple statements ----
    if ";" in sql_lower:
        raise ValueError("Multiple SQL statements are not allowed.")

    # ---- Must start with SELECT or WITH ----
    if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
        raise ValueError("Only SELECT queries are allowed.")

    # ---- Block forbidden keywords ----
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_lower):
            raise ValueError(f"Forbidden SQL keyword detected: {keyword.upper()}")

    # ---- Enforce LIMIT if missing ----
    if not re.search(r"\blimit\b", sql_lower):
        sql = f"{sql} LIMIT {default_limit}"

    return sql