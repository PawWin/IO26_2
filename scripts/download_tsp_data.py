from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BASE_URL = "https://raw.githubusercontent.com/mastqe/tsplib/master"
INSTANCES = {
    "lin318": 318,
    "pcb442": 442,
    "d493": 493,
    "rat575": 575,
    "pr1002": 1002,
}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, dimension in INSTANCES.items():
        path = DATA_DIR / f"{name}.tsp"
        if path.exists():
            print(f"{name}: istnieje, pomijam ({path})")
            continue
        text = _download_instance(name)
        _validate_instance(name, dimension, text)
        path.write_text(text, encoding="utf-8")
        print(f"{name}: pobrano ({path})")


def _download_instance(name: str) -> str:
    url = f"{BASE_URL}/{name}.tsp"
    try:
        with urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8")
    except URLError as error:
        raise SystemExit(f"{name}: nie udało się pobrać {url}: {error}") from error


def _validate_instance(name: str, expected_dimension: int, text: str) -> None:
    dimension = _metadata_value(text, "DIMENSION")
    if dimension != str(expected_dimension):
        raise SystemExit(
            f"{name}: niepoprawny DIMENSION={dimension!r}, oczekiwano {expected_dimension}."
        )
    if "NODE_COORD_SECTION" not in text:
        raise SystemExit(f"{name}: pobrany plik nie zawiera NODE_COORD_SECTION.")


def _metadata_value(text: str, key: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if ":" not in line:
            continue
        raw_key, value = line.split(":", 1)
        if raw_key.strip().upper() == key:
            return value.strip()
    return None


if __name__ == "__main__":
    main()
