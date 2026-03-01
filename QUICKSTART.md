# Quick Start Guide

## Uruchomienie aplikacji

### Sposób 1: Bezpośrednio z Pythona
```bash
python main.py
```

Lub jeśli używasz virtualenv:
```bash
.venv\Scripts\python.exe main.py
```

### Sposób 2: Podwójne kliknięcie
Po zbudowaniu .exe możesz po prostu kliknąć dwukrotnie na plik `MLBevo_LogViewer.exe`

## Testowanie aplikacji

1. Uruchom aplikację
2. Przeciągnij plik `sample_log.txt` do okna aplikacji
3. Sprawdź funkcjonalności:
   - ✅ Wyświetlanie metadanych (Serial Number, Test Result, Filtered Rows)
   - ✅ Tabela z 15 wierszami danych testowych
   - ✅ Wyszukiwanie - wpisz "voltage" w wyszukiwarkę
   - ✅ Sortowanie - kliknij nagłówki kolumn
   - ✅ Formatowanie hex - zobacz kolumny Lower/Upper Limit i Value

## Budowanie .exe

### Krok 1: Instalacja PyInstaller
```bash
pip install pyinstaller
```

### Krok 2: Budowanie
```bash
python build.py
```

Po zakończeniu znajdziesz plik `MLBevo_LogViewer.exe` w folderze `dist/`

### Krok 3: Testowanie .exe
```bash
dist\MLBevo_LogViewer.exe
```

## Rozmiar pliku .exe
- Pojedynczy plik: ~100-150 MB (zawiera całe środowisko Python + PyQt6)
- Można zmniejszyć używając UPX compression
- Nie wymaga instalacji Pythona na komputerze docelowym

## Porównanie z wersją React

| Cecha | React (oryginał) | Python (nowy) |
|-------|------------------|---------------|
| **Rozmiar** | ~5 MB (spakowany) | ~100 MB (standalone .exe) |
| **Uruchomienie** | Wymaga serwera/buildu | Kliknij i działaj |
| **Zależności** | Node.js, npm | Brak (w .exe) |
| **Platforma** | Przeglądarka | Windows native |
| **Wygląd** | Identyczny | Identyczny |
| **Funkcje** | Pełne | Pełne |
| **Build time** | ~30s (Vite) | ~15s (PyInstaller) |

## Dostosowanie

### Zmiana kolorów
Edytuj słownik `COLORS` w [main.py](main.py#L19-L37)

### Dodanie nowych kolumn
1. Zaktualizuj `TestRow` w [log_parser.py](log_parser.py#L15-L23)
2. Dodaj kolumnę w `COLUMNS` w [main.py](main.py#L274)
3. Dodaj logikę parsowania w `parse_log_file()`

### Zmiana formatu pliku
Edytuj funkcję `parse_log_file()` w [log_parser.py](log_parser.py#L75)

## Znane problemy

- PyQt6 na Windows może pokazywać warning o DPI scaling - można zignorować
- Pierwsze uruchomienie .exe może być wolniejsze (Windows Defender scan)
- Długie wartości hex w tabeli mogą wydłużyć wysokość wiersza

## Support

Dla problemów lub pytań: D. Piskorowski (AQP1)
