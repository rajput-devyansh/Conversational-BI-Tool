import re
from typing import List

def extract_tables_from_sql(sql: str) -> List[str]:
    """
    Naive but reliable table name extraction for SELECT queries.
    Works well for our controlled SQL generation.
    """
    if not sql:
        return []

    sql = sql.lower()

    matches = re.findall(
        r"(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql
    )

    seen = set()
    tables = []
    for t in matches:
        if t not in seen:
            seen.add(t)
            tables.append(t)

    return tables