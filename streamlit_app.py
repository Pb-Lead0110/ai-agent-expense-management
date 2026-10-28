import json
import os
import tempfile
import uuid

import streamlit as st

from app.agent import run_agent
from app.database import init_db
from app.tools import execute_sql_query

# Limit pytań na jedną sesję, żeby demo nie zużyło całego limitu API
MAX_QUESTIONS = 10

st.set_page_config(page_title="AI Agent wydatków domowych")

# Każdy odwiedzający dostaje własną kopię bazy z przykładowymi danymi,
# żeby jego INSERT/UPDATE nie zmieniały danych innym osobom
if "db_path" not in st.session_state:
    st.session_state.db_path = os.path.join(tempfile.gettempdir(), f"expenses_{uuid.uuid4().hex}.db")
    init_db(st.session_state.db_path)
    st.session_state.messages = []
    st.session_state.questions = 0

db_path = st.session_state.db_path


def show_steps(steps):
    """Pokazuje, jakich narzędzi i zapytań SQL użył agent."""
    if not steps:
        return
    with st.expander("Co zrobił agent"):
        for step in steps:
            if step["tool"] == "execute_sql_query":
                st.code(step["args"].get("query", ""), language="sql")
            else:
                st.write("Pobranie struktury tabeli (get_database_schema)")


st.title("AI Agent wydatków domowych")
st.write(
    "Zapytaj o domowe wydatki z września i października. Agent sam napisze zapytanie SQL, "
    "wykona je na bazie SQLite i odpowie po polsku."
)
st.caption("Agent nie pamięta poprzednich pytań - każde pytanie traktuje osobno.")

with st.sidebar:
    st.header("Dane w bazie")
    rows = json.loads(execute_sql_query("SELECT * FROM expenses;", db_path))
    st.dataframe(rows, hide_index=True)
    if st.button("Przywróć dane początkowe"):
        init_db(db_path)
        st.rerun()

    st.header("Przykładowe pytania")
    st.markdown(
        "- Ile wydaliśmy na jedzenie w październiku?\n"
        "- Na co poszło najwięcej pieniędzy we wrześniu?\n"
        "- Porównaj wydatki z września i października.\n"
        "- Dodaj wydatek: 45 zł na kawę z przyjaciółmi w kategorii Rozrywka.\n"
        "- Zmień kwotę wydatku o id 1 na 400 zł."
    )
    st.caption(f"Pozostało pytań: {MAX_QUESTIONS - st.session_state.questions} z {MAX_QUESTIONS}")
    st.markdown("[Kod na GitHubie](https://github.com/Pb-Lead0110/ai-agent-expense-management)")

# Historia rozmowy
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        show_steps(msg.get("steps"))

limit_reached = st.session_state.questions >= MAX_QUESTIONS
if limit_reached:
    st.info("Wykorzystano limit pytań w tej sesji. Projekt możesz uruchomić u siebie - instrukcja jest na GitHubie.")

question = st.chat_input("Np. Ile wydaliśmy na jedzenie?", disabled=limit_reached)

if question:
    st.session_state.questions += 1
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        steps = []
        with st.spinner("Agent analizuje zapytanie..."):
            try:
                answer = run_agent(question, db_path, steps) or "Brak odpowiedzi."
            except Exception as e:
                # Szczegóły tylko w logach, użytkownik widzi prosty komunikat
                print(f"Błąd API: {e}")
                answer = "Nie udało się uzyskać odpowiedzi (możliwy chwilowy limit API). Spróbuj za chwilę."

    st.session_state.messages.append({"role": "assistant", "content": answer, "steps": steps})
    # Odświeżenie strony, żeby tabela w panelu bocznym pokazała nowe dane
    st.rerun()
