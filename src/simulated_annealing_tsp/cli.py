from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from simulated_annealing_tsp.annealing import AnnealingConfig, SimulatedAnnealingTsp
from simulated_annealing_tsp.html_report import write_final_html_report, write_html_report
from simulated_annealing_tsp.operators import OPERATORS
from simulated_annealing_tsp.tsp import distance_matrix, load_tsplib

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Symulowane wyżarzanie dla instancji TSPLIB TSP.")
    parser.add_argument("--instance", default="lin318", help="Nazwa pliku z data/ bez .tsp albo ścieżka do .tsp.")
    parser.add_argument("--iterations", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--initial-temperature", type=float, default=850.0)
    parser.add_argument("--cooling-rate", type=float, default=0.9995)
    parser.add_argument("--minimum-temperature", type=float, default=0.01)
    parser.add_argument("--operators", nargs="+", choices=sorted(OPERATORS), default=list(OPERATORS))
    parser.add_argument("--frame-stride", type=int, default=50, help="Co którą iterację zapisać jako klatkę HTML.")
    parser.add_argument("--no-report", action="store_true", help="Uruchom obliczenia bez generowania raportów HTML.")
    parser.add_argument("--output", type=Path, help="Ścieżka wynikowego pliku HTML.")
    parser.add_argument("--all", action="store_true", help="Wygeneruj raporty HTML dla wszystkich plików z data/.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error("--iterations must be positive")
    if args.initial_temperature <= 0:
        parser.error("--initial-temperature must be positive")
    if not 0 < args.cooling_rate < 1:
        parser.error("--cooling-rate must be in (0, 1)")
    if args.minimum_temperature <= 0:
        parser.error("--minimum-temperature must be positive")
    if args.frame_stride < 1:
        parser.error("--frame-stride must be positive")

    paths = sorted(DATA_DIR.glob("*.tsp")) if args.all else [_resolve_instance(args.instance)]
    output_base = args.output if args.output is not None else ROOT / "results"

    completed_runs = []
    for path in paths:
        started_at = perf_counter()
        report_path = _report_path(output_base, path, multiple=args.all)
        instance = load_tsplib(path)
        engine = SimulatedAnnealingTsp(
            distance_matrix(instance),
            AnnealingConfig(
                initial_temperature=args.initial_temperature,
                cooling_rate=args.cooling_rate,
                minimum_temperature=args.minimum_temperature,
                max_iterations=args.iterations,
                seed=args.seed,
                operators=tuple(args.operators),
            ),
        )
        engine.run(args.iterations)
        elapsed = perf_counter() - started_at
        if args.no_report:
            print(f"{instance.name}: najlepszy_koszt={engine.state.best_distance}, czas={_format_seconds(elapsed)}")
        else:
            write_html_report(report_path, instance, engine.state, frame_stride=args.frame_stride)
            completed_runs.append((instance, engine.state))
            print(
                f"{instance.name}: najlepszy_koszt={engine.state.best_distance}, "
                f"czas={_format_seconds(elapsed)}, html={report_path}"
            )

    if args.all and not args.no_report:
        final_report_path = _final_report_path(output_base)
        write_final_html_report(final_report_path, completed_runs, frame_stride=args.frame_stride)
        print(f"raport końcowy: html={final_report_path}")


def _resolve_instance(instance: str) -> Path:
    path = Path(instance)
    if path.exists():
        return path
    bundled = DATA_DIR / f"{instance.removesuffix('.tsp')}.tsp"
    if bundled.exists():
        return bundled
    raise FileNotFoundError(f"Nie znaleziono instancji TSPLIB: {instance}")


def _report_path(output: Path, instance_path: Path, multiple: bool) -> Path:
    if output.suffix == ".html" and not multiple:
        return output
    return output / f"{instance_path.stem}_annealing.html"


def _final_report_path(output: Path) -> Path:
    if output.suffix == ".html":
        return output
    return output / "raport.html"


def _format_seconds(seconds: float) -> str:
    return f"{seconds:.3f}s"
