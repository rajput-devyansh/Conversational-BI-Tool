import pytest
from core.validation.sql_guard import validate_sql

def test_allows_simple_select():
    sql = "SELECT * FROM orders"
    validated = validate_sql(sql)

    assert validated.lower().startswith("select")
    assert "from orders" in validated.lower()
    assert "limit" in validated.lower()

def test_strips_markdown_fences():
    sql = """```sql
    SELECT COUNT(*) FROM orders
    ```"""
    cleaned = validate_sql(sql)
    assert cleaned.lower().startswith("select")
    assert "```" not in cleaned

def test_blocks_multiple_statements():
    sql = "SELECT * FROM orders; DROP TABLE orders;"
    with pytest.raises(ValueError):
        validate_sql(sql)

def test_blocks_delete():
    sql = "DELETE FROM orders"
    with pytest.raises(ValueError):
        validate_sql(sql)

def test_blocks_insert():
    sql = "INSERT INTO orders VALUES (1)"
    with pytest.raises(ValueError):
        validate_sql(sql)

def test_blocks_update():
    sql = "UPDATE orders SET price = 10"
    with pytest.raises(ValueError):
        validate_sql(sql)