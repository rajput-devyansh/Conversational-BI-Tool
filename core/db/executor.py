import time
import pandas as pd
from core.db.connection import get_connection

def execute_sql(query: str):
    start_time = time.time()

    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()

        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "success": True,
            "data": df,
            "error": None,
            "metadata": {
                "row_count": len(df),
                "execution_time_ms": round(elapsed_ms, 2)
            }
        }

    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "success": False,
            "data": None,
            "error": str(e),
            "metadata": {
                "row_count": 0,
                "execution_time_ms": round(elapsed_ms, 2)
            }
        }