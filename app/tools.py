import sqlite3
import json
from app.database import get_db_connection

def get_database_schema() -> str:
    """Zwraca opis struktury tabeli 'expenses' w bazie danych."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='expenses';")
    schema = cursor.fetchone()
    conn.close()
    
    if schema:
        return f"Struktura tabeli 'expenses':\n{schema[0]}"
    return "Tabela 'expenses' nie istnieje."


def execute_sql_query(query: str) -> str:
    """
    Wykonuje zapytanie SQL na bazie danych i zwraca wynik w formacie JSON
    lub komunikat o błędzie/sukcesie.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        # Jeśli zapytanie zwraca dane (SELECT, WITH ... SELECT itp.)
        # cursor.description jest ustawione tylko wtedy, gdy są kolumny wyniku
        if cursor.description is not None:
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            return json.dumps(results, ensure_ascii=False)
        
        # Jeśli zapytanie modyfikuje dane (INSERT, UPDATE, DELETE)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return f"Zapytanie wykonane pomyślnie. Zmieniono/dodano wierszy: {affected}."
        
    except sqlite3.Error as e:
        conn.close()
        return f"Błąd bazy danych SQL: {str(e)}"


# Słownik opisu narzędzi w formacie JSON Schema dla modeli LLM (OpenAI / Groq)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": "Pobiera schemat (składnię CREATE TABLE) tabeli wydatków w bazie danych.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql_query",
            "description": "Wykonuje zapytanie SQL (SELECT, INSERT, itp.) na bazie SQLite i zwraca wynik.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Poprawne zapytanie SQL w składni SQLite."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

if __name__ == "__main__":
    # Szybki test działania narzędzi
    print("--- TEST SCHEMATU ---")
    print(get_database_schema())
    
    print("\n--- TEST ZAPYTANIA SELECT ---")
    print(execute_sql_query("SELECT * FROM expenses LIMIT 2;"))