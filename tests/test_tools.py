import json
import pytest
from app import database
from app.tools import get_database_schema, execute_sql_query

@pytest.fixture(autouse=True)
def setup_test_database(tmp_path, monkeypatch):
    """Fixture tworzący osobną bazę w folderze tymczasowym, żeby testy nie kasowały expenses.db."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test_expenses.db"))
    database.init_db()
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
    data = json.loads(result)
    assert data[0]["total"] == 18  # Mamy 18 przykładowych wydatków w init_db

def test_execute_sql_query_sum_food():
    """Sprawdza sumę dla kategorii Jedzenie (ten sam przykład co w README)."""
    result = execute_sql_query("SELECT SUM(amount) as suma FROM expenses WHERE category = 'Jedzenie';")
    data = json.loads(result)
    assert data[0]["suma"] == pytest.approx(2126.70)

def test_execute_sql_query_with_cte():
    """Zapytanie zaczynające się od WITH też powinno zwrócić dane, a nie 'zmieniono wierszy'."""
    result = execute_sql_query(
        "WITH drogie AS (SELECT * FROM expenses WHERE amount > 1000) SELECT COUNT(*) as ile FROM drogie;"
    )
    data = json.loads(result)
    assert data[0]["ile"] == 2  # czynsz we wrześniu i październiku

def test_execute_sql_query_insert():
    """Sprawdza dodanie nowego rekordu przez zapytanie INSERT."""
    insert_query = """
    INSERT INTO expenses (category, amount, description)
    VALUES ('Jedzenie', 99.99, 'Testowe zakupy');
    """
    response = execute_sql_query(insert_query)
    assert "wykonane pomyślnie" in response

    # Weryfikacja w bazie
    select_res = execute_sql_query("SELECT * FROM expenses WHERE description = 'Testowe zakupy';")
    data = json.loads(select_res)
    assert len(data) == 1
    assert data[0]["amount"] == 99.99

def test_drop_table_is_blocked():
    """Agent nie może usunąć tabeli."""
    result = execute_sql_query("DROP TABLE expenses;")
    assert "zablokowane" in result
    # Tabela dalej istnieje
    assert "CREATE TABLE expenses" in get_database_schema()

def test_delete_is_blocked():
    """Agent nie może usuwać wydatków, także ukrytym DELETE po WITH."""
    assert "zablokowane" in execute_sql_query("DELETE FROM expenses;")
    assert "zablokowane" in execute_sql_query("WITH x AS (SELECT 1) DELETE FROM expenses;")

    data = json.loads(execute_sql_query("SELECT COUNT(*) as total FROM expenses;"))
    assert data[0]["total"] == 18

def test_insert_with_forbidden_word_in_text_is_allowed():
    """Słowa 'DROP' i 'DELETE' w opisie wydatku nie powinny blokować INSERT-a."""
    result = execute_sql_query(
        "INSERT INTO expenses (category, amount, description) VALUES ('Rozrywka', 39.90, 'Książka o SQL: DROP i DELETE');"
    )
    assert "wykonane pomyślnie" in result

def test_update_needs_where():
    """UPDATE z WHERE działa, a bez WHERE jest blokowany (zmieniłby wszystkie wydatki)."""
    assert "zablokowane" in execute_sql_query("UPDATE expenses SET amount = 0;")

    result = execute_sql_query("UPDATE expenses SET amount = 175 WHERE id = 1;")
    assert "wykonane pomyślnie" in result
    data = json.loads(execute_sql_query("SELECT amount FROM expenses WHERE id = 1;"))
    assert data[0]["amount"] == 175

def test_execute_sql_query_invalid_syntax():
    """Sprawdza, czy funkcja bezpiecznie wyłapuje błędy składni SQL."""
    result = execute_sql_query("SELECT * FROM non_existing_table;")
    assert "Błąd bazy danych SQL" in result
