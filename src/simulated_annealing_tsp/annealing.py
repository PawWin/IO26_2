from __future__ import annotations

from dataclasses import dataclass, field
from math import exp
from random import Random

from simulated_annealing_tsp.operators import OPERATORS
from simulated_annealing_tsp.tsp import route_length


@dataclass(frozen=True)
class AnnealingConfig:
    initial_temperature: float = 1200.0
    cooling_rate: float = 0.995
    minimum_temperature: float = 0.01
    max_iterations: int = 20_000
    seed: int = 123
    operators: tuple[str, ...] = tuple(OPERATORS)


@dataclass(frozen=True)
class StepResult:
    iteration: int
    temperature: float
    operator: str
    accepted: bool
    delta: int
    current_distance: int
    best_distance: int
    acceptance_probability: float


@dataclass
class AnnealingState:
    route: list[int]
    current_distance: int
    best_route: list[int]
    best_distance: int
    temperature: float
    iteration: int = 0
    finished: bool = False
    history: list[dict[str, int | float | str | bool | list[int]]] = field(default_factory=list)


class SimulatedAnnealingTsp:
    def __init__(self, matrix: list[list[int]], config: AnnealingConfig) -> None:
        if len(matrix) < 3:
            raise ValueError("TSP wymaga co najmniej 3 miast.")
        unknown = [name for name in config.operators if name not in OPERATORS]
        if unknown:
            raise ValueError(f"Nieznane operatory: {', '.join(unknown)}")

        self.matrix = matrix
        self.config = config
        self.rng = Random(config.seed)
        initial_route = nearest_neighbor_route(matrix, self.rng.randrange(len(matrix)))
        initial_distance = route_length(initial_route, matrix)
        self.state = AnnealingState(
            route=initial_route,
            current_distance=initial_distance,
            best_route=initial_route.copy(),
            best_distance=initial_distance,
            temperature=config.initial_temperature,
        )

    def step(self) -> StepResult:
        state = self.state
        if state.finished:
            return self._last_result()

        operator_name = self.rng.choice(self.config.operators)
        candidate_route, operation = OPERATORS[operator_name](state.route, self.rng)
        candidate_distance = route_length(candidate_route, self.matrix)
        delta = candidate_distance - state.current_distance
        probability = self.acceptance_probability(delta, state.temperature)
        accepted = delta <= 0 or self.rng.random() < probability

        if accepted:
            state.route = candidate_route
            state.current_distance = candidate_distance
            if candidate_distance < state.best_distance:
                state.best_distance = candidate_distance
                state.best_route = candidate_route.copy()

        state.iteration += 1
        state.temperature *= self.config.cooling_rate
        state.finished = (
            state.iteration >= self.config.max_iterations
            or state.temperature <= self.config.minimum_temperature
        )

        result = StepResult(
            iteration=state.iteration,
            temperature=state.temperature,
            operator=operation,
            accepted=accepted,
            delta=delta,
            current_distance=state.current_distance,
            best_distance=state.best_distance,
            acceptance_probability=probability,
        )
        row: dict[str, int | float | str | bool | list[int]] = result.__dict__.copy()
        row["current_route"] = state.route.copy()
        row["best_route"] = state.best_route.copy()
        state.history.append(row)
        return result

    def run(self, steps: int) -> StepResult:
        result = self._last_result()
        for _ in range(steps):
            result = self.step()
            if self.state.finished:
                break
        return result

    def two_opt_polish(self, max_passes: int = 50) -> None:
        for _ in range(max_passes):
            improved = False
            route = self.state.best_route
            size = len(route)
            for i in range(size - 1):
                for j in range(i + 2, size):
                    if i == 0 and j == size - 1:
                        continue
                    gain = self._two_opt_gain(route, i, j)
                    if gain < 0:
                        route[i + 1 : j + 1] = reversed(route[i + 1 : j + 1])
                        self.state.best_distance += gain
                        self.state.current_distance = self.state.best_distance
                        self.state.route = route.copy()
                        self.state.best_route = route.copy()
                        self._append_polish_step(i, j, gain)
                        improved = True
                        break
                if improved:
                    break
            if not improved:
                return

    def _two_opt_gain(self, route: list[int], i: int, j: int) -> int:
        a, b = route[i], route[(i + 1) % len(route)]
        c, d = route[j], route[(j + 1) % len(route)]
        return self.matrix[a][c] + self.matrix[b][d] - self.matrix[a][b] - self.matrix[c][d]

    def _append_polish_step(self, i: int, j: int, gain: int) -> None:
        self.state.iteration += 1
        row: dict[str, int | float | str | bool | list[int]] = {
            "iteration": self.state.iteration,
            "temperature": self.state.temperature,
            "operator": f"2-opt({i + 1}:{j})",
            "accepted": True,
            "delta": gain,
            "current_distance": self.state.current_distance,
            "best_distance": self.state.best_distance,
            "acceptance_probability": 1.0,
            "current_route": self.state.route.copy(),
            "best_route": self.state.best_route.copy(),
        }
        self.state.history.append(row)

    @staticmethod
    def acceptance_probability(delta: int, temperature: float) -> float:
        if delta <= 0:
            return 1.0
        if temperature <= 0:
            return 0.0
        return exp(-delta / temperature)

    def _last_result(self) -> StepResult:
        history = self.state.history
        if history:
            item = history[-1]
            return StepResult(
                iteration=int(item["iteration"]),
                temperature=float(item["temperature"]),
                operator=str(item["operator"]),
                accepted=bool(item["accepted"]),
                delta=int(item["delta"]),
                current_distance=int(item["current_distance"]),
                best_distance=int(item["best_distance"]),
                acceptance_probability=float(item["acceptance_probability"]),
            )
        return StepResult(
            iteration=0,
            temperature=self.state.temperature,
            operator="-",
            accepted=False,
            delta=0,
            current_distance=self.state.current_distance,
            best_distance=self.state.best_distance,
            acceptance_probability=0.0,
        )


def nearest_neighbor_route(matrix: list[list[int]], start: int = 0) -> list[int]:
    unvisited = set(range(len(matrix)))
    route = [start]
    unvisited.remove(start)
    while unvisited:
        current = route[-1]
        next_city = min(unvisited, key=lambda city: matrix[current][city])
        route.append(next_city)
        unvisited.remove(next_city)
    return route
