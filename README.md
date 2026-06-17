# Symulowane wyżarzanie dla TSP

Projekt realizuje zadanie: ręczna implementacja algorytmu symulowanego wyżarzania z wizualizacją i symulacją krokową dla pięciu instancji z TSPLIB.

## Uruchomienie

```bash
uv sync
uv run sa-tsp --instance berlin52 --iterations 20000 --output results/berlin52.html
```

Wygenerowany plik HTML otwórz w przeglądarce:


Wygenerowanie raportów dla wszystkich pięciu zestawów:

```bash
uv run sa-tsp --all --iterations 20000 --frame-stride 50 --output results
```

## Zakres

- parser plików TSPLIB `.tsp`;
- pięć gotowych zestawów danych w `data/`: `berlin52`, `eil51`, `st70`, `kroA100`, `pr76`;
- własna implementacja symulowanego wyżarzania bez bibliotek optymalizacyjnych;
- pięć operatorów zmiany trasy: `swap`, `reverse`, `insert`, `scramble`, `block_insert`;
- start z trasy konstrukcyjnej najbliższego sąsiada oraz opcjonalne końcowe dopracowanie `2-opt`;
- wynikowy plik HTML z Plotly.js, animacją, suwakiem iteracji i przyciskami Play/Pause;
- wizualizacja najlepszej znalezionej trasy w kolejnych krokach algorytmu.

Plotly jest używane wyłącznie do eksportu wizualizacji HTML.