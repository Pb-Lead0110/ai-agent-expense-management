import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.tools import get_database_schema, execute_sql_query, TOOLS_SCHEMA

# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Inicjalizacja klienta OpenAI/Groq
# Domyślnie używamy darmowego i bardzo szybkiego API Groq z modelem Llama 3.3 / Llama 3.1
api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = "https://api.groq.com/openai/v1" if os.getenv("GROQ_API_KEY") else None
model_name = "openai/gpt-oss-20b" if os.getenv("GROQ_API_KEY") else "gpt-4o-mini"

client = OpenAI(api_key=api_key, base_url=base_url)

SYSTEM_PROMPT = """
Jesteś pomocnym asystentem AI ds. analizy wydatków w firmie.
Twoim zadaniem jest odpowiadanie na pytania użytkownika dotyczące wydatków.

ZASADY:
1. Jeśli nie znasz dokładnej struktury tabeli w bazie danych, użyj narzędzia `get_database_schema`.
2. Do odpytania bazy użyj narzędzia `execute_sql_query` z poprawną składnią SQLite.
3. Gdy otrzymasz wyniki w formacie JSON z bazy danych, przeanalizuj je i daj zwięzłą, czytelną odpowiedź po polsku.
4. Zawsze podawaj kwoty w PLN.
"""

def run_agent(user_query: str) -> str:
    """
    Główna pętla decyzyjna agenta (Agentic Loop).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    # Limit kroków, aby agent nie wpadł w nieskończoną pętlę
    max_turns = 5

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        # 1. Sprawdzamy, czy model zdecydował się wywołać narzędzie (Tool Calling)
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"🤖 [AGENT ACTION]: Wywołuję narzędzie `{function_name}` z argumentami: {function_args}")

                # Wykonanie odpowiedniej funkcji w Pythonie
                if function_name == "get_database_schema":
                    tool_output = get_database_schema()
                elif function_name == "execute_sql_query":
                    tool_output = execute_sql_query(function_args.get("query"))
                else:
                    tool_output = "Błąd: Nieznana funkcja."

                # Przekazanie wyniku narzędzia z powrotem do konwersacji z LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_output)
                })
        else:
            # 2. Jeśli model nie wywołuje już narzędzi, zwraca ostateczną odpowiedź dla użytkownika
            return response_message.content

    return "Agent osiągnął maksymalną liczbę kroków bez podania odpowiedzi."


if __name__ == "__main__":
    # Testowy zapis do sprawdzenia w konsoli
    print("--- START TESTU AGENTA ---")
    query = "Ile łącznie wydaliśmy na kategorię Software?"
    print(f"Pytanie użytkownika: {query}\n")
    
    result = run_agent(query)
    print("\nOstateczna odpowiedź agenta:")
    print(result)