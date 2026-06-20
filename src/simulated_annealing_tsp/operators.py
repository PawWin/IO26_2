from __future__ import annotations

from collections.abc import Callable
from random import Random

RouteOperator = Callable[[list[int], Random], tuple[list[int], str]]


def swap_cities(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    i, j = sorted(rng.sample(range(len(route)), 2))
    candidate[i], candidate[j] = candidate[j], candidate[i]
    return candidate, f"swap({i}, {j})"


def reverse_segment(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    i, j = sorted(rng.sample(range(len(route)), 2))
    candidate[i : j + 1] = reversed(candidate[i : j + 1])
    return candidate, f"reverse({i}:{j})"


def two_opt_move(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    size = len(route)
    while True:
        i, j = sorted(rng.sample(range(size), 2))
        if j > i + 1 and not (i == 0 and j == size - 1):
            break
    candidate[i + 1 : j + 1] = reversed(candidate[i + 1 : j + 1])
    return candidate, f"2-opt({i + 1}:{j})"


def insert_city(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    i, j = rng.sample(range(len(route)), 2)
    city = candidate.pop(i)
    candidate.insert(j, city)
    return candidate, f"insert({i}->{j})"


OPERATORS: dict[str, RouteOperator] = {
    "two_opt": two_opt_move,
    "swap": swap_cities,
    "reverse": reverse_segment,
    "insert": insert_city,
}
