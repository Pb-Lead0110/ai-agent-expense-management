# AI Agent wydatków domowych

Agent AI w Pythonie, który odpowiada na pytania o domowe wydatki zadawane zwykłym językiem, np. „Ile wydaliśmy na jedzenie w październiku?”. Model sam decyduje, jakie zapytanie SQL wykonać na bazie SQLite (wzorzec **tool calling**), a potem podsumowuje wynik po polsku.

**Demo online:** https://ai-agent-expense-management-jo7vhae2stttkaplwf6ucy.streamlit.app/ - można przetestować bez instalacji i bez klucza API.

## Jak to działa

1. Użytkownik zadaje pytanie w konsoli albo na stronie.
2. Model dostaje pytanie oraz dwa narzędzia:
   - `get_database_schema` - zwraca strukturę tabeli `expenses`,
   - `execute_sql_query` - wykonuje zapytanie SQL i zwraca wynik w JSON.
3. Agent wywołuje narzędzia tyle razy, ile potrzebuje (maksymalnie 5 kroków), i zwraca odpowiedź.

```mermaid
sequenceDiagram
    actor Użytkownik
    participant Agent as Agent (LLM)
    participant Tools as Narzędzia (tools.py)
    participant DB as SQLite (expenses.db)

    Użytkownik->>Agent: "Ile wydaliśmy na jedzenie?"
    Agent->>Tools: get_database_schema()
    Tools-->>Agent: CREATE TABLE expenses (...)
    Agent->>Tools: execute_sql_query("SELECT SUM(amount) ...")
    Tools->>DB: zapytanie SQL
    DB-->>Tools: wynik
    Tools-->>Agent: [{"suma": 2126.7}]
    Agent-->>Użytkownik: "Na jedzenie wydaliście łącznie 2126,70 PLN."
```

## Technologie

- Python 3.11+
- OpenAI SDK - Groq API (model `openai/gpt-oss-20b`) albo OpenAI API (model `gpt-4o-mini`)
- SQLite
- Streamlit (wersja webowa)
- pytest
- Docker, Docker Compose

## Struktura projektu

- `app/agent.py` - pętla agenta i komunikacja z modelem
- `app/database.py` - tworzenie bazy i przykładowe wydatki
- `app/main.py` - wersja w konsoli
- `app/tools.py` - narzędzia dla modelu i sprawdzanie zapytań SQL
- `streamlit_app.py` - wersja webowa (demo)
- `tests/test_tools.py` - testy

## Konfiguracja

Skopiuj `.env.example` do `.env` i uzupełnij jeden z kluczy:

| Zmienna | Skąd wziąć |
| :--- | :--- |
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) (darmowy) |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

Jeśli podasz oba klucze, używany jest Groq.

## Uruchomienie

### Docker

```bash
git clone https://github.com/Pb-Lead0110/ai-agent-expense-management.git
cd ai-agent-expense-management
cp .env.example .env
docker compose build
docker compose run --rm expense-agent
```

Baza jest tworzona przy budowaniu obrazu. Dane dodane w kontenerze znikają po jego zamknięciu.

### Lokalnie

```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m app.database
python -m app.main
```

`python -m app.database` tworzy plik `expenses.db` z 18 przykładowymi wydatkami domowymi z września i października. Ponowne uruchomienie przywraca dane początkowe.

### Wersja webowa (lokalnie)

Po instalacji zależności i uzupełnieniu `.env`:

```bash
streamlit run streamlit_app.py
```

Strona otworzy się pod adresem `http://localhost:8501`. Każda sesja w przeglądarce dostaje własną kopię bazy z przykładowymi danymi, więc nie zmienia `expenses.db`.

## Przykładowe pytania

- Ile wydaliśmy na jedzenie w październiku?
- Na co poszło najwięcej pieniędzy we wrześniu?
- Porównaj wydatki z września i października.
- Pokaż 3 największe wydatki.
- Dodaj wydatek: 45 zł na kawę z przyjaciółmi w kategorii Rozrywka.
- Zmień kwotę wydatku o id 1 na 400 zł.

Aby zakończyć, wpisz `exit` albo `q`.

## Zabezpieczenia

Zapytania SQL pisze model, więc przed wykonaniem każde jest sprawdzane w `tools.py`:

- dozwolone są tylko zapytania zaczynające się od `SELECT`, `WITH`, `INSERT` i `UPDATE`,
- `UPDATE` musi mieć `WHERE`, żeby nie zmienić wszystkich wierszy naraz,
- blokowane są m.in. `DROP`, `DELETE`, `ALTER`, `CREATE`, `PRAGMA`,
- SQLite nie wykona kilku zapytań naraz (np. `SELECT ...; DROP TABLE ...`).

W wersji demo dodatkowo każdy odwiedzający ma własną, tymczasową bazę, a liczba pytań jest ograniczona do 10 na sesję.

To proste zabezpieczenie oparte na słowach kluczowych, wystarczające w projekcie demonstracyjnym. W prawdziwej aplikacji agent powinien łączyć się z bazą przez osobnego użytkownika z ograniczonymi uprawnieniami.

## Testy

```bash
pytest
```

Testy działają na tymczasowej bazie, więc nie zmieniają `expenses.db`. Sprawdzają narzędzia bazodanowe i blokowanie niebezpiecznych zapytań. Nie wywołują API modelu, więc nie potrzebują klucza.
