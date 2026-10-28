import sys
from app.agent import run_agent

def main():
    print("=" * 50)
    print("  🤖 AGENT WYDATKÓW DOMOWYCH")
    print("=" * 50)
    print("Zadaj pytanie dotyczące wydatków domowych.")
    print("Przykłady:")
    print("  - Ile wydaliśmy na jedzenie w październiku?")
    print("  - Porównaj wydatki z września i października.")
    print("  - Dodaj wydatek: 45 zł na kawę z przyjaciółmi w kategorii Rozrywka.")
    print("Wpisz 'exit' lub 'q', aby zakończyć.\n")

    while True:
        try:
            user_input = input("\nTy > ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "q", "quit", "koniec", "wyjdź"]:
                print("\nDo widzenia!")
                break

            print("\n⏳ Agent analizuje zapytanie...")
            response = run_agent(user_input)
            
            print(f"\nAgent > {response}\n")
            print("-" * 50)
            
        except (KeyboardInterrupt, EOFError):
            print("\nPrzerwano działanie programu. Do widzenia!")
            sys.exit(0)
        except Exception as e:
            # Np. brak internetu, zły klucz API albo limit zapytań - nie wywalamy całego programu
            print(f"\n❌ Wystąpił błąd: {e}")
            print("Spróbuj ponownie.")

if __name__ == "__main__":
    main()