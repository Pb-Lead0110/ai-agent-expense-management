import sqlite3
import pytest
from app.database import init_db, DB_PATH
from app.tools import get_database_schema, execute_sql_query

@pytest.fixture(autouse=True)
def setup_test_database():
    """Fixture przygotowujący świeżą bazę danych przed każdym testem."""
    init_db()
    yield

def test_get_database_schema():
    """Sprawdza, czy funkcja zwraca schemat tabeli expenses."""
    schema = get_database_schema()
    assert "CREATE TABLE expenses" in schema
    assert "category" in schema
    assert "amount" in schema

def test_execute_sql_query_select():
    """Sprawdza wykonanie poprawnego zapytania SELECT."""
    result = execute_sql_query("SELECT COUNT(*) as total FROM expenses;")
    assert "total" in result
    assert "6" in result  # Mamy 6 przykładowych rekordów w init_db

def test_execute_sql_query_insert():
    """Sprawdza dodanie nowego rekordu przez zapytanie INSERT."""
    insert_query = """
    INSERT INTO expenses (category, amount, description) 
    VALUES ('Software', 99.99, 'Testowa subskrypcja');
    """
    response = execute_sql_query(insert_query)
    assert "wykonane pomyślnie" in response

    # Weryfikacja w bazie
    select_res = execute_sql_query("SELECT * FROM expenses WHERE description = 'Testowa subskrypcja';")
    assert "99.99" in select_res

def test_execute_sql_query_invalid_syntax():
    """Sprawdza, czy funkcja bezpiecznie wyłapuje błędy składni SQL."""
    result = execute_sql_query("SELECT * FROM non_existing_table;")
    assert "Błąd bazy danych SQL" in result