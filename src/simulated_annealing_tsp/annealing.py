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
        initial_route = random_route(len(matrix), self.rng)
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


def random_route(size: int, rng: Random) -> list[int]:
    route = list(range(size))
    rng.shuffle(route)
    return route
