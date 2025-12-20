from core.validation.sql_guard import validate_sql
from core.db.executor import execute_sql
from core.chains.text_to_sql import create_text_to_sql_chain

def create_sql_agent(llm):
    text_to_sql = create_text_to_sql_chain(llm)

    def answer_question(question: str, max_retries: int = 2):
        last_error = None
        sql = None

        for attempt in range(1, max_retries + 2):
            try:
                # 1. Generate SQL
                if last_error:
                    augmented_question = (
                        f"{question}\n\n"
                        f"The previous SQL query failed with this error:\n"
                        f"{last_error}\n\n"
                        f"Please correct the SQL."
                    )
                else:
                    augmented_question = question

                sql = text_to_sql(augmented_question)

                # 2. Validate SQL
                safe_sql = validate_sql(sql)

                # 3. Execute SQL
                result = execute_sql(safe_sql)

                if result["success"]:
                    return {
                        "success": True,
                        "sql": safe_sql,
                        "data": result["data"],
                        "error": None,
                        "attempts": attempt
                    }

                last_error = result["error"]

            except Exception as e:
                last_error = str(e)

        return {
            "success": False,
            "sql": sql,
            "data": None,
            "error": last_error,
            "attempts": max_retries + 1
        }

    return answer_question