# MLBevo Log Viewer (Python)

Aplikacja desktopowa do przeglądania i analizowania logów testowych MLBevo Door Module. Wersja Python z interfejsem PyQt6.

## Funkcjonalności

- 📁 **Drag & Drop**: Przeciągnij i upuść pliki logów (.txt, .csv, .log)
- 📊 **Wyświetlanie Metadanych**: Numer seryjny, wynik testu, liczba wierszy
- 🔍 **Wyszukiwanie**: Szybkie wyszukiwanie w tabeli wyników
- ⬆️⬇️ **Sortowanie**: Sortowanie po dowolnej kolumnie przez kliknięcie nagłówka
- 🎨 **Kolorowe Statusy**: Wizualne rozróżnienie wyników (PASS/FAIL/WARN)
- 💾 **Format Hex**: Automatyczne formatowanie długich wartości hex

## Instalacja

### Wymagania
- Python 3.8 lub nowszy

### Krok 1: Instalacja zależności

```bash
pip install -r requirements.txt
```

### Krok 2: Uruchomienie aplikacji

```bash
python main.py
```

## Budowanie pliku .exe

Aby stworzyć standalone plik .exe, użyj PyInstaller:

### Krok 1: Instalacja PyInstaller

```bash
pip install pyinstaller
```

### Krok 2: Budowanie .exe

```bash
python build.py
```

Alternatywnie, ręcznie:

```bash
pyinstaller --onefile --windowed --name "MLBevo_LogViewer" --icon=icon.ico main.py
```

Plik .exe zostanie utworzony w folderze `dist/`.

## Użycie

1. Uruchom aplikację
2. Przeciągnij plik logu do okna lub kliknij, aby wybrać plik
3. Przeglądaj wyniki w tabeli
4. Użyj wyszukiwarki do filtrowania wyników
5. Kliknij nagłówek kolumny, aby posortować dane
6. Kliknij "Load another file", aby załadować kolejny plik

## Format Plików

Aplikacja akceptuje pliki CSV z następującą strukturą:

- **Linia 1**: Metadane (Serialnumber, Testresult)
- **Linia 2**: Nagłówki kolumn (oddzielone średnikiem)
- **Linie 3+**: Dane testowe

Wymagane kolumny:
- ExternalId
- Text
- LowerLimit
- Value
- UpperLimit
- Unit
- Result
- StatusText

## Struktura Projektu

```
MLBevo_viewer/
├── main.py              # Główna aplikacja GUI
├── log_parser.py        # Parser plików logów
├── requirements.txt     # Zależności Python
├── build.py            # Skrypt do budowania .exe
├── README.md           # Ten plik
└── mlbevo-log-viewer/  # Oryginalne repozytorium React
```

## Różnice względem wersji React

- ✅ Identyczna funkcjonalność parsowania logów
- ✅ Identyczny układ i kolory interfejsu
- ✅ Identyczne wymiary i spacing
- ✅ Desktop app - nie wymaga przeglądarki
- ✅ Szybsze ładowanie i mniejszy rozmiar
- ✅ Łatwa konwersja do .exe

## Możliwości rozwoju

- [ ] Eksport wyników do Excel/CSV
- [ ] Wykresy i statystyki
- [ ] Porównywanie logów
- [ ] Historia ostatnich plików
- [ ] Dark mode
- [ ] Drukowanie raportów

## Autor

Designed for AQP1 by D. Piskorowski

## Licencja

Prywatny projekt dla AQP1
