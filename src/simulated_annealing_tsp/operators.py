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


def insert_city(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    i, j = rng.sample(range(len(route)), 2)
    city = candidate.pop(i)
    candidate.insert(j, city)
    return candidate, f"insert({i}->{j})"


def scramble_segment(route: list[int], rng: Random) -> tuple[list[int], str]:
    candidate = route.copy()
    i, j = sorted(rng.sample(range(len(route)), 2))
    segment = candidate[i : j + 1]
    rng.shuffle(segment)
    candidate[i : j + 1] = segment
    return candidate, f"scramble({i}:{j})"


def block_insert(route: list[int], rng: Random) -> tuple[list[int], str]:
    segment_length = rng.randint(2, len(route) - 1)
    i = rng.randrange(len(route) - segment_length + 1)
    j = i + segment_length - 1
    segment = route[i : j + 1]
    remainder = route[:i] + route[j + 1 :]
    insertion_points = [index for index in range(len(remainder) + 1) if index != i]
    k = rng.choice(insertion_points)
    candidate = remainder[:k] + segment + remainder[k:]
    return candidate, f"block_insert({i}:{j}->{k})"


OPERATORS: dict[str, RouteOperator] = {
    "swap": swap_cities,
    "reverse": reverse_segment,
    "insert": insert_city,
    "scramble": scramble_segment,
    "block_insert": block_insert,
}
