from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

import plotly.graph_objects as go

from simulated_annealing_tsp.annealing import AnnealingState
from simulated_annealing_tsp.tsp import TspInstance

HistoryRow = dict[str, int | float | str | bool | list[int]]

PAPER = "#f6f2ea"
INK = "#1f2421"
MUTED = "#665f55"
ACCENT = "#d94f30"
CURRENT = "#2563eb"
BEST = "#c6281d"
PANEL = "#fffaf1"
BORDER = "#d0bea7"

OPTIMAL_TOUR_LENGTHS = {
    "lin318": 42029,
    "pcb442": 50778,
    "d493": 35002,
    "rat575": 6773,
    "pr1002": 259045,
}


@dataclass(frozen=True)
class ReportRun:
    instance: TspInstance
    state: AnnealingState
    frame_stride: int


def write_html_report(
    path: Path,
    instance: TspInstance,
    state: AnnealingState,
    frame_stride: int = 1,
) -> None:
    run = ReportRun(instance=instance, state=state, frame_stride=frame_stride)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = _document(
        title=f"Symulowane wyżarzanie TSP - {escape(instance.name)}",
        subtitle=(
            f"{instance.dimension} miast, EDGE_WEIGHT_TYPE={escape(instance.edge_weight_type)}, "
            f"najlepsza długość={state.best_distance}, iteracje={state.iteration}"
        ),
        sections=[_run_section(run, 0, include_plotlyjs=True)],
    )
    path.write_text(html, encoding="utf-8")


def write_final_html_report(
    path: Path,
    runs: list[tuple[TspInstance, AnnealingState]],
    frame_stride: int = 1,
) -> None:
    if not runs:
        raise ValueError("Brak przebiegów do raportu zbiorczego.")
    path.parent.mkdir(parents=True, exist_ok=True)
    report_runs = [
        ReportRun(instance=instance, state=state, frame_stride=frame_stride)
        for instance, state in runs
    ]
    sections = [
        _run_section(run, index, include_plotlyjs=index == 0)
        for index, run in enumerate(report_runs)
    ]
    html = _document(
        title="Raport zadania 2: symulowane wyżarzanie dla TSP",
        subtitle=(
            "Raport zawiera wszystkie uruchomione instancje TSPLIB. Każda sekcja ma "
            "symulację krokową najlepszej trasy z podglądem trasy poprawiającej wynik, "
            "wykres kosztu oraz temperatury, podsumowanie i tabelę kroków dodawaną "
            "podczas animacji."
        ),
        sections=sections,
    )
    path.write_text(html, encoding="utf-8")


def _run_section(run: ReportRun, index: int, include_plotlyjs: bool) -> str:
    _validate_run(run)
    sampled_history = _sample_history(run.state.history, run.frame_stride)
    prefix = f"annealing-{index}"
    route_html = _route_figure(run.instance, run.state.history, run.frame_stride).to_html(
        include_plotlyjs=include_plotlyjs,
        full_html=False,
        div_id=f"{prefix}-route",
        config={"responsive": True, "displaylogo": False},
    )
    progress_html = _progress_figure(run.instance, run.state.history).to_html(
        include_plotlyjs=False,
        full_html=False,
        div_id=f"{prefix}-progress",
        config={"responsive": True, "displaylogo": False},
    )
    return f"""
        <section class="run-section">
            <div class="section-heading">
                <h2>{escape(run.instance.name)}</h2>
            </div>
            {_summary_table(run.instance, run.state)}
            <h3>Symulacja krokowa trasy</h3>
            <div class="plot-wrap">{route_html}</div>
            <h3>Wykres kosztu trasy i temperatury</h3>
            <div class="plot-wrap plot-wrap-compact">{progress_html}</div>
            {_operator_table(run.state)}
            {_steps_table(prefix, run.instance, sampled_history)}
        </section>
    """


def _document(title: str, subtitle: str, sections: list[str]) -> str:
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
        :root {{
            --paper: {PAPER};
            --panel: {PANEL};
            --ink: {INK};
            --muted: {MUTED};
            --accent: {ACCENT};
            --current: {CURRENT};
            --best: {BEST};
            --border: {BORDER};
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: var(--paper);
            color: var(--ink);
            font-family: Georgia, 'Times New Roman', serif;
            overflow-anchor: none;
        }}
        .report-header,
        .run-section {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 26px 28px;
        }}
        .report-header {{
            border-bottom: 1px solid rgba(31, 36, 33, 0.1);
        }}
        h1, h2, h3 {{
            margin: 0;
            line-height: 1.12;
            letter-spacing: 0;
        }}
        h1 {{ font-size: 34px; }}
        h2 {{ font-size: 28px; }}
        h3 {{
            margin-top: 26px;
            font-size: 18px;
        }}
        p {{
            margin: 7px 0 0;
            color: var(--muted);
            line-height: 1.48;
        }}
        .run-section + .run-section {{
            border-top: 1px solid rgba(31, 36, 33, 0.14);
        }}
        .section-heading {{
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 18px;
            margin-bottom: 16px;
        }}
        .plot-wrap {{
            margin-top: 10px;
            background: rgba(255, 250, 241, 0.48);
            border: 1px solid rgba(208, 190, 167, 0.58);
            border-radius: 8px;
            overflow: hidden;
        }}
        .plot-wrap-compact {{
            margin-bottom: 22px;
        }}
        .table-panel {{
            margin: 16px 0 0;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        .table-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 13px 16px;
            border-bottom: 1px solid var(--border);
        }}
        .table-toolbar h3 {{
            margin: 0;
        }}
        .table-toolbar button {{
            appearance: none;
            border: 1px solid var(--border);
            border-radius: 7px;
            background: #f6efe3;
            color: var(--ink);
            padding: 7px 10px;
            font: inherit;
            cursor: pointer;
        }}
        .table-toolbar button:hover {{
            border-color: var(--ink);
        }}
        .table-wrap {{
            max-height: 310px;
            overflow: auto;
            overflow-anchor: none;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th, td {{
            padding: 9px 12px;
            border-bottom: 1px solid rgba(208, 190, 167, 0.74);
            text-align: right;
            white-space: nowrap;
        }}
        th {{
            position: sticky;
            top: 0;
            z-index: 1;
            background: #efe5d6;
            color: var(--muted);
            font-weight: 700;
        }}
        .summary-table th,
        .summary-table td,
        .operator-table th,
        .operator-table td {{
            text-align: left;
        }}
        .steps-table th:nth-child(2), .steps-table td:nth-child(2),
        .steps-table th:nth-child(3), .steps-table td:nth-child(3) {{
            text-align: left;
        }}
        tbody tr:last-child td {{
            border-bottom: 0;
        }}
        tbody tr.is-new {{
            animation: row-flash 0.8s ease-out;
        }}
        .accepted {{
            color: #206a38;
            font-weight: 700;
        }}
        .rejected {{
            color: #9b2f1f;
            font-weight: 700;
        }}
        .empty-row td {{
            color: var(--muted);
            text-align: left;
            padding: 16px;
        }}
        @media (max-width: 720px) {{
            .report-header,
            .run-section {{
                padding: 22px 14px;
            }}
            .section-heading {{
                display: block;
            }}
            h1 {{ font-size: 27px; }}
            h2 {{ font-size: 24px; }}
        }}
        @keyframes row-flash {{
            from {{ background: rgba(217, 79, 48, 0.18); }}
            to {{ background: transparent; }}
        }}
    </style>
</head>
<body>
    <header class="report-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </header>
    <main>
        {"".join(sections)}
    </main>
    <script>
        function restorePageScroll(x, y) {{
            window.scrollTo(x, y);
            requestAnimationFrame(() => window.scrollTo(x, y));
        }}

        function decisionCell(row) {{
            return row.accepted
                ? "<span class='accepted'>zaakceptowano</span>"
                : "<span class='rejected'>odrzucono</span>";
        }}

        document.querySelectorAll("[data-steps-panel]").forEach((panel) => {{
            const rows = JSON.parse(panel.dataset.rows);
            const rowsByIteration = new Map(rows.map((row) => [String(row.iteration), row]));
            const inserted = new Set();
            const body = panel.querySelector("[data-steps-body]");
            const clearButton = panel.querySelector("[data-clear-steps]");
            const plot = document.getElementById(panel.dataset.plotId);

            function addStep(iteration) {{
                const key = String(iteration);
                const row = rowsByIteration.get(key);
                if (!row || inserted.has(key)) {{
                    return;
                }}
                const scrollX = window.scrollX;
                const scrollY = window.scrollY;
                const empty = body.querySelector(".empty-row");
                if (empty) {{
                    empty.remove();
                }}
                inserted.add(key);
                const tr = document.createElement("tr");
                tr.className = "is-new";
                tr.innerHTML = `
                    <td>${{row.iteration}}</td>
                    <td>${{row.operator}}</td>
                    <td>${{decisionCell(row)}}</td>
                    <td>${{row.delta}}</td>
                    <td>${{row.current_distance}}</td>
                    <td>${{row.current_optimum_gap}}</td>
                    <td>${{row.best_distance}}</td>
                    <td>${{row.best_optimum_gap}}</td>
                    <td>${{Number(row.temperature).toFixed(4)}}</td>
                `;
                body.appendChild(tr);
                restorePageScroll(scrollX, scrollY);
            }}

            function clearSteps() {{
                inserted.clear();
                body.innerHTML = "<tr class='empty-row'><td colspan='9'>Uruchom animację albo przesuń suwak, aby dodawać kroki.</td></tr>";
            }}

            clearButton.addEventListener("click", clearSteps);
            if (plot) {{
                plot.on("plotly_sliderchange", (event) => {{
                    if (event && event.step && event.step.label) {{
                        addStep(event.step.label);
                    }}
                }});
                plot.on("plotly_animatingframe", (event) => {{
                    if (event && event.name) {{
                        addStep(event.name);
                    }} else if (event && event.frame && event.frame.name) {{
                        addStep(event.frame.name);
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>
"""


def _route_figure(instance: TspInstance, history: list[HistoryRow], frame_stride: int) -> go.Figure:
    visual_frames = _route_visual_frames(instance.name, history, frame_stride)
    first = visual_frames[0]
    figure = go.Figure(
        data=[
            _city_trace(instance),
            _maybe_route_trace(instance, first["current_route"], "Aktualna trasa", CURRENT, 2.0),
            _route_trace(instance, first["best_route"], "Najlepsza trasa", BEST, 3.0),
        ],
        frames=[
            go.Frame(
                data=[
                    _city_trace(instance),
                    _maybe_route_trace(instance, row["current_route"], "Aktualna trasa", CURRENT, 2.0),
                    _route_trace(instance, row["best_route"], "Najlepsza trasa", BEST, 3.0),
                ],
                name=row["name"],
                layout=go.Layout(title=row["title"]),
            )
            for row in visual_frames
        ],
    )
    figure.update_layout(
        title=first["title"],
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"color": INK, "family": "Georgia, Times New Roman, serif"},
        height=720,
        margin={"l": 20, "r": 20, "t": 92, "b": 52},
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "xanchor": "right", "x": 1},
        xaxis={"visible": False, "scaleanchor": "y", "scaleratio": 1},
        yaxis={"visible": False},
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 1,
                "y": 1.16,
                "xanchor": "right",
                "yanchor": "top",
                "bgcolor": PANEL,
                "bordercolor": BORDER,
                "borderwidth": 1,
                "font": {"color": INK, "size": 13},
                "pad": {"r": 8, "t": 4},
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 180, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"},
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "y": -0.04,
                "currentvalue": {"prefix": "Iteracja: ", "font": {"color": INK}},
                "steps": [
                    {
                        "label": row["label"],
                        "method": "animate",
                        "args": [
                            [row["name"]],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    }
                    for row in visual_frames
                ],
            }
        ],
    )
    return figure


def _progress_figure(instance: TspInstance, history: list[HistoryRow]) -> go.Figure:
    iterations = [int(row["iteration"]) for row in history]
    current_distance = [int(row["current_distance"]) for row in history]
    best_distance = [int(row["best_distance"]) for row in history]
    temperatures = [float(row["temperature"]) for row in history]

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=iterations,
            y=current_distance,
            mode="lines",
            name="Aktualny koszt",
            line={"color": CURRENT, "width": 1.7},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=iterations,
            y=best_distance,
            mode="lines",
            name="Najlepszy koszt",
            line={"color": BEST, "width": 2.4},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=iterations,
            y=temperatures,
            mode="lines",
            name="Temperatura",
            yaxis="y2",
            line={"color": ACCENT, "width": 1.7, "dash": "dot"},
        )
    )
    figure.update_layout(
        title=f"{instance.name}: koszt trasy i temperatura",
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"color": INK, "family": "Georgia, Times New Roman, serif"},
        height=430,
        margin={"l": 64, "r": 70, "t": 66, "b": 54},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        xaxis={"title": "Iteracja", "gridcolor": "rgba(31, 36, 33, 0.12)"},
        yaxis={"title": "Koszt trasy", "gridcolor": "rgba(31, 36, 33, 0.12)"},
        yaxis2={"title": "Temperatura", "overlaying": "y", "side": "right"},
    )
    return figure


def _route_visual_frames(
    instance_name: str,
    history: list[HistoryRow],
    frame_stride: int,
) -> list[dict[str, str | int | list[int] | None]]:
    sampled_iterations = {int(row["iteration"]) for row in _sample_history(history, frame_stride)}
    frames: list[dict[str, str | int | list[int] | None]] = []
    previous_best_route = _route_from(history[0], "best_route")
    previous_best_distance = int(history[0]["best_distance"])

    for index, row in enumerate(history):
        iteration = int(row["iteration"])
        best_distance = int(row["best_distance"])
        improved = index > 0 and best_distance < previous_best_distance

        if improved:
            frames.append(
                {
                    "name": f"{iteration}-preview",
                    "label": f"{iteration} przed",
                    "iteration": iteration,
                    "current_route": _route_from(row, "current_route"),
                    "best_route": previous_best_route,
                    "title": _preview_title(instance_name, row, previous_best_distance),
                }
            )

        if iteration in sampled_iterations or improved:
            frames.append(
                {
                    "name": str(iteration),
                    "label": str(iteration),
                    "iteration": iteration,
                    "current_route": None,
                    "best_route": _route_from(row, "best_route"),
                    "title": _title(instance_name, row),
                }
            )

        previous_best_route = _route_from(row, "best_route")
        previous_best_distance = best_distance

    return frames


def _summary_table(instance: TspInstance, state: AnnealingState) -> str:
    initial = _initial_distance(state.history)
    optimum = _optimal_tour_length(instance)
    accepted = sum(1 for row in state.history if bool(row["accepted"]))
    all_steps = len(state.history)
    acceptance_rate = accepted / all_steps if all_steps else 0.0
    improvement = (initial - state.best_distance) / initial if initial else 0.0
    rows = [
        ("Liczba miast", str(instance.dimension)),
        ("Liczba iteracji", str(state.iteration)),
        ("Koszt początkowy", str(initial)),
        ("Najlepszy znaleziony koszt", str(state.best_distance)),
        ("Optimum", str(optimum) if optimum is not None else "brak danych"),
        ("Odległość najlepszego od optimum", _optimum_gap(state.best_distance, optimum)),
        ("Poprawa względem startu", _percent(improvement)),
        ("Zaakceptowane ruchy", f"{accepted} / {all_steps}"),
        ("Odsetek akceptacji", _percent(acceptance_rate)),
    ]
    return f"""
        <div class="stats-grid">
            <div class="table-panel">
                <div class="table-toolbar"><h3>Podsumowanie</h3></div>
                <table class="summary-table" aria-label="Podsumowanie {escape(instance.name)}">
                    <tbody>
                        {"".join(f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows)}
                    </tbody>
                </table>
            </div>
        </div>
    """


def _operator_table(state: AnnealingState) -> str:
    stats: dict[str, dict[str, int]] = {}
    for row in state.history:
        operator = _operator_name(str(row["operator"]))
        bucket = stats.setdefault(operator, {"used": 0, "accepted": 0})
        bucket["used"] += 1
        if bool(row["accepted"]):
            bucket["accepted"] += 1

    rows = []
    for operator, values in sorted(stats.items()):
        used = values["used"]
        accepted = values["accepted"]
        rows.append(
            "<tr>"
            f"<td>{escape(operator)}</td>"
            f"<td>{used}</td>"
            f"<td>{accepted}</td>"
            f"<td>{_percent(accepted / used if used else 0.0)}</td>"
            "</tr>"
        )
    return f"""
        <div class="table-panel">
            <div class="table-toolbar"><h3>Statystyki operatorów</h3></div>
            <div class="table-wrap">
                <table class="operator-table">
                    <thead>
                        <tr>
                            <th>Operator</th>
                            <th>Użycia</th>
                            <th>Zaakceptowane</th>
                            <th>Odsetek akceptacji</th>
                        </tr>
                    </thead>
                    <tbody>{"".join(rows)}</tbody>
                </table>
            </div>
        </div>
    """


def _steps_table(prefix: str, instance: TspInstance, sampled_history: list[HistoryRow]) -> str:
    optimum = _optimal_tour_length(instance)
    table_rows = [
        {
            "iteration": row["iteration"],
            "operator": row["operator"],
            "accepted": row["accepted"],
            "delta": row["delta"],
            "current_distance": row["current_distance"],
            "current_optimum_gap": _optimum_gap(int(row["current_distance"]), optimum),
            "best_distance": row["best_distance"],
            "best_optimum_gap": _optimum_gap(int(row["best_distance"]), optimum),
            "temperature": round(float(row["temperature"]), 4),
        }
        for row in sampled_history
    ]
    rows_json = escape(json.dumps(table_rows, ensure_ascii=False), quote=True)
    return f"""
        <div
            class="table-panel"
            data-steps-panel
            data-plot-id="{prefix}-route"
            data-rows="{rows_json}"
            aria-label="Historia kroków algorytmu"
        >
            <div class="table-toolbar">
                <h3>Historia kroków</h3>
                <button data-clear-steps type="button">Wyczyść tabelę</button>
            </div>
            <div class="table-wrap">
                <table class="steps-table">
                    <thead>
                        <tr>
                            <th>Iteracja</th>
                            <th>Operator</th>
                            <th>Decyzja</th>
                            <th>Delta</th>
                            <th>Aktualna</th>
                            <th>Aktualna do optimum</th>
                            <th>Najlepsza</th>
                            <th>Najlepsza do optimum</th>
                            <th>Temperatura</th>
                        </tr>
                    </thead>
                    <tbody data-steps-body>
                        <tr class="empty-row"><td colspan="9">Uruchom animację albo przesuń suwak, aby dodawać kroki.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    """


def _maybe_route_trace(
    instance: TspInstance,
    route: list[int] | None,
    name: str,
    color: str,
    width: float,
) -> go.Scatter:
    if route is None:
        return go.Scatter(
            x=[],
            y=[],
            mode="lines",
            line={"color": color, "width": width},
            hoverinfo="skip",
            name=name,
        )
    return _route_trace(instance, route, name, color, width)


def _route_trace(
    instance: TspInstance,
    route: list[int],
    name: str,
    color: str,
    width: float,
) -> go.Scatter:
    cities = list(instance.cities)
    ordered = [cities[index] for index in route] + [cities[route[0]]]
    return go.Scatter(
        x=[city.x for city in ordered],
        y=[city.y for city in ordered],
        mode="lines",
        line={"color": color, "width": width},
        hoverinfo="skip",
        name=name,
    )


def _city_trace(instance: TspInstance) -> go.Scatter:
    cities = list(instance.cities)
    return go.Scatter(
        x=[city.x for city in cities],
        y=[city.y for city in cities],
        mode="markers+text",
        marker={"size": 8, "color": ACCENT, "line": {"color": INK, "width": 1}},
        text=[str(city.index) for city in cities],
        textposition="top center",
        textfont={"size": 10, "color": INK},
        customdata=[city.index for city in cities],
        hovertemplate="miasto %{customdata}<br>x=%{x}<br>y=%{y}<extra></extra>",
        name="Miasta",
    )


def _sample_history(history: list[HistoryRow], frame_stride: int) -> list[HistoryRow]:
    if frame_stride < 1:
        raise ValueError("frame_stride musi być >= 1.")
    sampled = history[::frame_stride]
    if sampled[-1] is not history[-1]:
        sampled.append(history[-1])
    return sampled


def _route_from(row: HistoryRow, key: str) -> list[int]:
    route = row[key]
    if not isinstance(route, list):
        raise ValueError(f"Historia nie zawiera trasy {key}.")
    return route


def _initial_distance(history: list[HistoryRow]) -> int:
    first = history[0]
    current = int(first["current_distance"])
    delta = int(first["delta"])
    return current - delta if bool(first["accepted"]) else current


def _operator_name(value: str) -> str:
    return value.split("(", 1)[0]


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _optimal_tour_length(instance: TspInstance) -> int | None:
    return OPTIMAL_TOUR_LENGTHS.get(instance.name)


def _optimum_gap(distance: int, optimum: int | None) -> str:
    if optimum is None:
        return "brak danych"
    return _percent((distance - optimum) / optimum)


def _title(instance_name: str, row: HistoryRow) -> str:
    accepted = "zaakceptowano" if row["accepted"] else "odrzucono"
    return (
        f"{instance_name}: iteracja {row['iteration']} | best={row['best_distance']} | "
        f"current={row['current_distance']} | T={float(row['temperature']):.4f} | "
        f"{row['operator']} ({accepted}, delta={row['delta']})"
    )


def _preview_title(instance_name: str, row: HistoryRow, previous_best_distance: int) -> str:
    return (
        f"{instance_name}: iteracja {row['iteration']} | podgląd lepszej trasy | "
        f"poprzednia najlepsza={previous_best_distance} | nowa={row['best_distance']} | "
        f"{row['operator']} (delta={row['delta']})"
    )


def _validate_run(run: ReportRun) -> None:
    if not run.state.history:
        raise ValueError("Brak historii algorytmu do wizualizacji.")
    if run.frame_stride < 1:
        raise ValueError("frame_stride musi być >= 1.")
