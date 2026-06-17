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

W projekcie przygotowano obsługę pięciu instancji:

- `berlin52`
- `eil51`
- `st70`
- `pr76`
- `kroA100`

## Krótki opis realizacji

Główna logika algorytmu znajduje się w module
`src/simulated_annealing_tsp/annealing.py`. Parser plików TSPLIB oraz obliczanie
odległości są zaimplementowane w `src/simulated_annealing_tsp/tsp.py`, natomiast
operatory modyfikujące trasę znajdują się w `src/simulated_annealing_tsp/operators.py`.

Algorytm rozpoczyna działanie od utworzenia trasy początkowej metodą najbliższego
sąsiada. Następnie w każdej iteracji losowany jest jeden z operatorów zmiany trasy:

- zamiana dwóch miast (`swap`),
- odwrócenie fragmentu trasy (`reverse`),
- przeniesienie jednego miasta w inne miejsce (`insert`),
- wymieszanie fragmentu trasy (`scramble`),
- przeniesienie bloku miast (`block_insert`).


Po zakończeniu właściwego symulowanego wyżarzania program może dodatkowo wykonać
końcowe dopracowanie najlepszej trasy metodą `2-opt`. Na końcu generowany jest
raport HTML z animacją kolejnych kroków oraz tabelą historii działania algorytmu.

## Pseudokod algorytmu

```text
wczytaj plik TSPLIB
odczytaj listę miast i ich współrzędne
zbuduj macierz odległości między każdą parą miast

wybierz losowe miasto startowe
utwórz trasę początkową metodą najbliższego sąsiada
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

jeżeli włączono końcowe dopracowanie:
    wykonuj ulepszenia 2-opt na najlepszej trasie,
    dopóki można skrócić trasę albo osiągnięto limit przebiegów

zapisz najlepszą znalezioną trasę i historię działania do raportu HTML
```

## Dane wejściowe i wyjściowe

Dane wejściowe to pliki `.tsp` w katalogu `data/`.

Dane wyjściowe to pliki HTML w katalogu `results/`. Raport zawiera:

- nazwę instancji,
- liczbę miast,
- najlepszą znalezioną długość trasy,
- animację najlepszej trasy w kolejnych krokach,
- tabelę z historią iteracji, użytymi operatorami, zmianą kosztu i temperaturą.

