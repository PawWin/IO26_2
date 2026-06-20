# Realizacja zadania

## Autor

Projekt został zrealizowany indywidualnie przez:

Paweł Winkler


## Temat projektu

Projekt dotyczy rozwiązania problemu komiwojażera (TSP, Travelling Salesman Problem)
przy użyciu algorytmu symulowanego wyżarzania. Program wczytuje instancje problemu
z plików TSPLIB `.tsp`, buduje macierz odległości między miastami, uruchamia
algorytm optymalizacyjny, a następnie zapisuje wynik w postaci interaktywnego
raportu HTML.

W projekcie przygotowano obsługę pięciu instancji z co najmniej 300 miastami:

- `lin318`
- `pcb442`
- `d493`
- `rat575`
- `pr1002`

## Krótki opis realizacji

Główna logika algorytmu znajduje się w module
`src/simulated_annealing_tsp/annealing.py`. Parser plików TSPLIB oraz obliczanie
odległości są zaimplementowane w `src/simulated_annealing_tsp/tsp.py`, natomiast
operatory modyfikujące trasę znajdują się w `src/simulated_annealing_tsp/operators.py`.

Algorytm rozpoczyna działanie od utworzenia losowej trasy początkowej.
Następnie w każdej iteracji losowany jest jeden z operatorów zmiany trasy:

- zamiana dwóch miast (`swap`),
- ruch 2-opt odwracający fragment trasy po usunięciu dwóch krawędzi (`two_opt`),
- odwrócenie fragmentu trasy (`reverse`),
- przeniesienie jednego miasta w inne miejsce (`insert`).

Po zakończeniu symulowanego wyżarzania generowany jest raport HTML z animacją
kolejnych kroków oraz tabelą historii działania algorytmu.

## Pseudokod algorytmu

```text
wczytaj plik TSPLIB
odczytaj listę miast i ich współrzędne
zbuduj macierz odległości między każdą parą miast

utwórz losową permutację miast jako trasę początkową
oblicz długość trasy początkowej

aktualna_trasa = trasa_początkowa
najlepsza_trasa = trasa_początkowa
aktualny_koszt = długość trasy początkowej
najlepszy_koszt = aktualny_koszt
temperatura = temperatura_początkowa
iteracja = 0

dopóki iteracja < maksymalna_liczba_iteracji
    oraz temperatura > minimalna_temperatura:

    wylosuj operator zmiany trasy
    kandydat = zastosuj operator do aktualnej trasy
    koszt_kandydata = długość trasy kandydującej
    delta = koszt_kandydata - aktualny_koszt

    jeżeli delta <= 0:
        zaakceptuj kandydata
    w przeciwnym razie:
        prawdopodobieństwo = exp(-delta / temperatura)
        wylosuj liczbę z przedziału [0, 1)
        jeżeli liczba < prawdopodobieństwo:
            zaakceptuj kandydata
        w przeciwnym razie:
            odrzuć kandydata

    jeżeli kandydat został zaakceptowany:
        aktualna_trasa = kandydat
        aktualny_koszt = koszt_kandydata

        jeżeli aktualny_koszt < najlepszy_koszt:
            najlepsza_trasa = aktualna_trasa
            najlepszy_koszt = aktualny_koszt

    zapisz informacje o iteracji do historii
    temperatura = temperatura * współczynnik_chłodzenia
    iteracja = iteracja + 1

zapisz najlepszą znalezioną trasę i historię działania do raportu HTML
```

## Dane wejściowe i wyjściowe

Dane wejściowe to pliki `.tsp` w katalogu `data/`.

Dane wyjściowe to pliki HTML w katalogu `results/`. Raport zawiera:

- nazwę instancji,
- liczbę miast,
- najlepszą znalezioną długość trasy,
- znane optimum i procentową odległość znalezionych kosztów od optimum,
- animację najlepszej trasy w kolejnych krokach,
- tabelę z historią iteracji, użytymi operatorami, zmianą kosztu i temperaturą.
