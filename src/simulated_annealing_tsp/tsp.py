from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, sqrt
from pathlib import Path


@dataclass(frozen=True)
class City:
    index: int
    x: float
    y: float


@dataclass(frozen=True)
class TspInstance:
    name: str
    dimension: int
    edge_weight_type: str
    cities: tuple[City, ...]
    source: str = ""


def parse_tsplib(text: str, source: str = "") -> TspInstance:
    metadata: dict[str, str] = {}
    cities: list[City] = []
    in_coords = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "EOF":
            continue
        if line == "NODE_COORD_SECTION":
            in_coords = True
            continue
        if in_coords:
            parts = line.split()
            if len(parts) < 3:
                continue
            cities.append(City(int(parts[0]), float(parts[1]), float(parts[2])))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().upper()] = value.strip()

    if not cities:
        raise ValueError("Plik TSPLIB nie zawiera sekcji NODE_COORD_SECTION.")

    dimension = int(metadata.get("DIMENSION", len(cities)))
    if dimension != len(cities):
        raise ValueError(f"DIMENSION={dimension}, ale odczytano {len(cities)} miast.")

    return TspInstance(
        name=metadata.get("NAME", Path(source).stem if source else "uploaded"),
        dimension=dimension,
        edge_weight_type=metadata.get("EDGE_WEIGHT_TYPE", "EUC_2D"),
        cities=tuple(sorted(cities, key=lambda city: city.index)),
        source=source,
    )


def load_tsplib(path: Path) -> TspInstance:
    return parse_tsplib(path.read_text(encoding="utf-8"), source=str(path))


def distance_matrix(instance: TspInstance) -> list[list[int]]:
    cities = instance.cities
    matrix = [[0 for _ in cities] for _ in cities]
    for i, city_a in enumerate(cities):
        for j in range(i + 1, len(cities)):
            distance = tsp_distance(city_a, cities[j], instance.edge_weight_type)
            matrix[i][j] = distance
            matrix[j][i] = distance
    return matrix


def tsp_distance(a: City, b: City, edge_weight_type: str) -> int:
    match edge_weight_type:
        case "EUC_2D":
            return int(sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2) + 0.5)
        case "CEIL_2D":
            return int(sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2) + 0.999999999)
        case "ATT":
            rij = sqrt(((a.x - b.x) ** 2 + (a.y - b.y) ** 2) / 10.0)
            tij = int(rij + 0.5)
            return tij if tij >= rij else tij + 1
        case "GEO":
            return geo_distance(a, b)
        case _:
            raise ValueError(f"Nieobsługiwany EDGE_WEIGHT_TYPE: {edge_weight_type}")


def geo_distance(a: City, b: City) -> int:
    lat_a, lon_a = _geo_to_radians(a.x), _geo_to_radians(a.y)
    lat_b, lon_b = _geo_to_radians(b.x), _geo_to_radians(b.y)
    q1 = cos(lon_a - lon_b)
    q2 = cos(lat_a - lat_b)
    q3 = cos(lat_a + lat_b)
    return int(6378.388 * acos(0.5 * ((1.0 + q1) * q2 - (1.0 - q1) * q3)) + 1.0)


def _geo_to_radians(value: float) -> float:
    degrees = int(value)
    minutes = value - degrees
    return pi * (degrees + 5.0 * minutes / 3.0) / 180.0


def route_length(route: list[int], matrix: list[list[int]]) -> int:
    total = 0
    for i, city in enumerate(route):
        total += matrix[city][route[(i + 1) % len(route)]]
    return total
