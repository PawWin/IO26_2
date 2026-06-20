# Symulowane wyżarzanie dla TSP

Projekt realizuje implementacje algorytmu symulowanego wyżarzania z wizualizacją i symulacją krokową dla pięciu instancji z TSPLIB.

## Uruchomienie

```bash
uv sync
uv run python scripts/download_tsp_data.py
uv run sa-tsp --instance lin318 --iterations 20000 --output results/lin318.html
```

Wygenerowany plik HTML otwórz w przeglądarce.

Skrypt `scripts/download_tsp_data.py` pobiera brakujące instancje TSPLIB do
`data/` i pomija pliki, które już istnieją.

Wygenerowanie raportów dla wszystkich pięciu zestawów:

```bash
uv run sa-tsp --all --iterations 20000 --frame-stride 50 --output results
```

Polecenie utworzy raporty dla pojedynczych instancji oraz zbiorczy raport
`results/raport.html`.

Uruchomienie obliczeń bez generowania raportów HTML:

```bash
uv run sa-tsp --all --iterations 20000 --no-report
```

W tym trybie program wypisuje dla każdej instancji najlepszy znaleziony koszt
oraz czas obliczeń.

## Zakres

- parser plików TSPLIB `.tsp`;
- pięć gotowych zestawów danych w `data/` z co najmniej 300 miastami:
  `lin318`, `pcb442`, `d493`, `rat575`, `pr1002`;
- własna implementacja symulowanego wyżarzania bez bibliotek optymalizacyjnych;
- cztery operatory zmiany trasy: `two_opt`, `swap`, `reverse`, `insert`;
- start z losowej permutacji miast;
- wynikowy plik HTML z Plotly.js, animacją, suwakiem iteracji i przyciskami Play/Pause;
- wizualizacja najlepszej znalezionej trasy w kolejnych krokach algorytmu;
- raport zbiorczy `raport.html` dla wszystkich uruchomionych instancji, zawierający
  symulacje krokowe, wykresy kosztu i temperatury oraz tabele statystyk,
  w tym procentową odległość znalezionych kosztów od znanego optimum.

Plotly jest używane wyłącznie do eksportu wizualizacji HTML.
