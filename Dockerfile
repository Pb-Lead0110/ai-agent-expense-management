FROM python:3.11-slim

WORKDIR /app

# Kopiowanie zależności i ich instalacja
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie całego kodu źródłowego
COPY . .

# Inicjalizacja bazy danych przy budowaniu kontenera
RUN python -m app.database

# Domyślna komenda uruchamiająca aplikację
CMD ["python", "-m", "app.main"]