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

    # Przykładowe wydatki domowe z dwóch miesięcy
    sample_data = [
        # Wrzesień
        ("Jedzenie", 486.20, "Zakupy spożywcze - pierwsza połowa miesiąca", "2026-09-02"),
        ("Rachunki", 1850.00, "Czynsz za mieszkanie", "2026-09-05"),
        ("Rachunki", 289.00, "Rachunek za prąd", "2026-09-10"),
        ("Rachunki", 79.99, "Internet", "2026-09-12"),
        ("Transport", 320.00, "Paliwo", "2026-09-15"),
        ("Jedzenie", 512.80, "Zakupy spożywcze - druga połowa miesiąca", "2026-09-16"),
        ("Rozrywka", 64.00, "Kino we dwoje", "2026-09-20"),
        ("Zdrowie", 85.50, "Leki z apteki", "2026-09-24"),
        ("Zdrowie", 250.00, "Wizyta u dentysty", "2026-09-26"),
        # Październik
        ("Transport", 159.00, "Bilet miesięczny", "2026-10-01"),
        ("Jedzenie", 468.90, "Zakupy spożywcze - pierwsza połowa miesiąca", "2026-10-02"),
        ("Rachunki", 1850.00, "Czynsz za mieszkanie", "2026-10-05"),
        ("Rachunki", 79.99, "Internet", "2026-10-12"),
        ("Rozrywka", 43.00, "Abonament streamingowy", "2026-10-14"),
        ("Jedzenie", 530.40, "Zakupy spożywcze - druga połowa miesiąca", "2026-10-16"),
        ("Zdrowie", 120.00, "Badania krwi", "2026-10-20"),
        ("Jedzenie", 128.40, "Zakupy na urodziny", "2026-10-21"),
        ("Zdrowie", 54.90, "Witaminy", "2026-10-22")
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