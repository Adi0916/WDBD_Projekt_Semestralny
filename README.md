# OpenSky Network SQL
## Opis projektu
System służy do automatycznego gromadzenia i analizy danych o ruchu lotniczym w czasie rzeczywistym przy użyciu **OpenSky Network API**. Projekt realizuje pełny proces ETL (Extract, Transform, Load) – od pobrania danych przez API, przez ich walidację i archiwizację w relacyjnej bazie danych, aż po wizualizację na dashboardzie.

## Stos technologiczny
* **Baza danych:** PostgreSQL (Relacyjna struktura danych)
* **Język programowania:** Python 3.13.5 (Import danych, obsługa API)
* **API:** [OpenSky Network REST API](https://opensky-network.org/apidoc/rest.html)
* **Wizualizacja:** (do rozstrzygnięcia)
* **Biblioteki Python:** (do rozstrzygnięcia)
  
### Encje i tabele: (przykład)
* **Tabele merytoryczne (4):**
    * `flights` – dane o aktualnych lotach (pozycja, wysokość, prędkość).
    * `aircrafts` – szczegółowe informacje o statkach powietrznych (icao24, callsign).
    * `trajectories` – historia zmian pozycji dla poszczególnych lotów.
    * `flight_stats` – zagregowane metryki dotyczące lotów.
* **Tabela słownikowa (1):**
    * `countries` – słownik krajów pochodzenia statków powietrznych.
* **Tabela techniczna (1):**
    * `import_log` – logowanie każdego cyklu pobierania danych (timestamp, status, liczba rekordów, czas trwania).

## Funkcje systemu (przykład)
- [x] **Cykliczny import:** Automatyczne odpytywanie API w interwale czasowym (np. co 5 minut).
- [x] **Historyczność:** System nie nadpisuje danych, lecz buduje historię lotów.
- [x] **Brak duplikacji:** Mechanizmy sprawdzające unikalność rekordów przed zapisem do bazy.
- [x] **Analiza SQL:** Zestaw 5 zaawansowanych zapytań (np. top 5 najaktywniejszych krajów, średnia wysokość przelotowa w danym regionie).

## Wizualizacja i Filtrowanie (przykład)
Projekt zawiera warstwę wizualizacyjną z **3 różnymi wykresami** oraz rozbudowanym systemem filtracji (**10 filtrów**), takimi jak:
1.  Kraj pochodzenia
2.  Zakres wysokości (Altitude)
3.  Prędkość (Velocity)
4.  Przynależność do strefy (Longitude/Latitude)
5.  ...i inne.

## Struktura plików (przykład)
```text
├── sql/
│   ├── schema.sql           # Definicja tabel, kluczy i więzów integralności
│   └── analysis.sql         # 5 wymaganych zapytań raportowych
├── src/
│   ├── main.py              # Główny skrypt uruchamiający import
│   ├── database.py          # Logika połączenia i zapisu do DB
│   └── api_client.py        # Obsługa zapytań do OpenSky Network
├── docs/
│   └── erd_diagram.png      # Wizualny model bazy danych
├── .env.example             # Przykład pliku konfiguracyjnego (API keys, DB pass)
└── README.md
```

## Instalacja i Konfiguracja (przykład)

Projekt wykorzystuje menedżer **uv**, który gwarantuje błyskawiczną instalację i identyczne środowisko u każdego członka zespołu.

### 1. Instalacja `uv`
Jeśli nie masz jeszcze `uv`, zainstaluj go poniższym poleceniem:

* **macOS / Linux:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
* **Windows (PowerShell):**
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 2. Pobranie i przygotowanie projektu
```bash
# Sklonuj repozytorium

git clone https://github.com/Adi0916/OpenSky_Network_SQL
cd WDBD_Projekt_Semestralny

# Automatyczna instalacja Pythona i wszystkich zależności
uv sync
```
