import sqlite3
import os

# Baza zawsze w głównym folderze projektu, niezależnie skąd uruchomimy skrypt
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "expenses.db")

def get_db_connection(db_path=None):
    """Tworzy połączenie z bazą danych SQLite (domyślnie expenses.db)."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row  # Pozwala na dostęp do kolumn po nazwach
    return conn

def init_db(db_path=None):
    """Tworzy tabelę i usuwa stary plik bazy, jeśli istnieje."""
    db_path = db_path or DB_PATH
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Tworzenie tabeli wydatków
    cursor.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            date TEXT DEFAULT CURRENT_DATE
        )
    """)

    # Przykładowe dane
    sample_data = [
        ("Software", 150.00, "Licencja GitHub Copilot", "2026-10-01"),
        ("Software", 200.00, "Subskrypcja OpenAI API", "2026-10-05"),
        ("Travel", 450.50, "Bilet kolejowy Warszawa - Kraków", "2026-10-10"),
        ("Food", 120.00, "Obiad biznesowy z klientem Acme", "2026-10-12"),
        ("Hardware", 1200.00, "Monitor do pracy zdalnej", "2026-10-15"),
        ("Software", 50.00, "Domena i hosting", "2026-10-18")
    ]

    cursor.executemany("""
        INSERT INTO expenses (category, amount, description, date)
        VALUES (?, ?, ?, ?)
    """, sample_data)

    conn.commit()
    conn.close()
    print("Baza danych została pomyślnie utworzona i wypełniona danymi!")

if __name__ == "__main__":
    init_db()