from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go

from simulated_annealing_tsp.annealing import AnnealingState
from simulated_annealing_tsp.tsp import TspInstance

PAPER = "#f6f2ea"
INK = "#1f2421"
MUTED = "#665f55"
ACCENT = "#d94f30"
PANEL = "#fffaf1"
BORDER = "#d0bea7"


def write_html_report(
    path: Path,
    instance: TspInstance,
    state: AnnealingState,
    frame_stride: int = 1,
) -> None:
    if not state.history:
        raise ValueError("Brak historii algorytmu do wizualizacji.")
    if frame_stride < 1:
        raise ValueError("frame_stride musi być >= 1.")

    path.parent.mkdir(parents=True, exist_ok=True)
    sampled_history = state.history[::frame_stride]
    if sampled_history[-1] is not state.history[-1]:
        sampled_history.append(state.history[-1])

    first = sampled_history[0]
    figure = go.Figure(
        data=[
            _route_trace(instance, _route_from(first, "best_route")),
            _city_trace(instance),
        ],
        frames=[
            go.Frame(
                data=[
                    _route_trace(instance, _route_from(row, "best_route")),
                    _city_trace(instance),
                ],
                name=str(row["iteration"]),
                layout=go.Layout(title=_title(instance.name, row)),
            )
            for row in sampled_history
        ],
    )
    figure.update_layout(
        title=_title(instance.name, first),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"color": INK, "family": "Georgia, Times New Roman, serif"},
        height=720,
        margin={"l": 20, "r": 20, "t": 92, "b": 42},
        showlegend=False,
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
                            {"frame": {"duration": 180, "redraw": True}, "fromcurrent": True},
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
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
                        "label": str(row["iteration"]),
                        "method": "animate",
                        "args": [
                            [str(row["iteration"])],
                            {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"},
                        ],
                    }
                    for row in sampled_history
                ],
            }
        ],
    )
    html = _document(
        plot_html=figure.to_html(include_plotlyjs=True, full_html=False, div_id="annealing-plot"),
        instance=instance,
        state=state,
        sampled_history=sampled_history,
    )
    path.write_text(html, encoding="utf-8")


def _document(
    plot_html: str,
    instance: TspInstance,
    state: AnnealingState,
    sampled_history: list[dict[str, int | float | str | bool | list[int]]],
) -> str:
    table_rows = [
        {
            "iteration": row["iteration"],
            "operator": row["operator"],
            "accepted": row["accepted"],
            "delta": row["delta"],
            "current_distance": row["current_distance"],
            "best_distance": row["best_distance"],
            "temperature": round(float(row["temperature"]), 4),
        }
        for row in sampled_history
    ]
    rows_json = json.dumps(table_rows, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Symulowane wyżarzanie TSP - {instance.name}</title>
    <style>
        :root {{
            --paper: {PAPER};
            --panel: {PANEL};
            --ink: {INK};
            --muted: {MUTED};
            --accent: {ACCENT};
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
        .report-header {{
            padding: 24px 28px 8px;
            border-bottom: 1px solid rgba(31, 36, 33, 0.08);
        }}
        .report-header h1 {{
            margin: 0 0 6px;
            font-size: 32px;
            line-height: 1.12;
            letter-spacing: 0;
        }}
        .report-header p {{
            margin: 0;
            color: var(--muted);
        }}
        .plot-wrap {{
            padding: 0 12px;
        }}
        .steps-panel {{
            margin: 0 28px 34px;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        .steps-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 13px 16px;
            border-bottom: 1px solid var(--border);
        }}
        .steps-toolbar h2 {{
            margin: 0;
            font-size: 18px;
            letter-spacing: 0;
        }}
        .steps-toolbar button {{
            appearance: none;
            border: 1px solid var(--border);
            border-radius: 7px;
            background: #f6efe3;
            color: var(--ink);
            padding: 7px 10px;
            font: inherit;
            cursor: pointer;
        }}
        .steps-toolbar button:hover {{
            border-color: var(--ink);
        }}
        .steps-table-wrap {{
            max-height: 280px;
            overflow: auto;
            overflow-anchor: none;
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
            background: #efe5d6;
            color: var(--muted);
            font-weight: 700;
        }}
        th:nth-child(2), td:nth-child(2),
        th:nth-child(3), td:nth-child(3) {{
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
        @keyframes row-flash {{
            from {{ background: rgba(217, 79, 48, 0.18); }}
            to {{ background: transparent; }}
        }}
    </style>
</head>
<body>
    <header class="report-header">
        <h1>Symulowane wyżarzanie TSP - {instance.name}</h1>
        <p>{instance.dimension} miast, EDGE_WEIGHT_TYPE={instance.edge_weight_type}, najlepsza długość={state.best_distance}, iteracje={state.iteration}</p>
    </header>
    <main>
        <section class="plot-wrap">
            {plot_html}
        </section>
        <section class="steps-panel" aria-label="Historia kroków algorytmu">
            <div class="steps-toolbar">
                <h2>Historia kroków</h2>
                <button id="clear-steps" type="button">Wyczyść tabelę</button>
            </div>
            <div class="steps-table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Iteracja</th>
                            <th>Operator</th>
                            <th>Decyzja</th>
                            <th>Delta</th>
                            <th>Aktualna</th>
                            <th>Najlepsza</th>
                            <th>Temperatura</th>
                        </tr>
                    </thead>
                    <tbody id="steps-body">
                        <tr class="empty-row"><td colspan="7">Uruchom animację albo przesuń suwak, aby dodawać kroki.</td></tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>
    <script>
        const annealingRows = {rows_json};
        const rowsByIteration = new Map(annealingRows.map((row) => [String(row.iteration), row]));
        const inserted = new Set();
        const body = document.getElementById("steps-body");
        const clearButton = document.getElementById("clear-steps");
        const plot = document.getElementById("annealing-plot");

        function restorePageScroll(x, y) {{
            window.scrollTo(x, y);
            requestAnimationFrame(() => window.scrollTo(x, y));
        }}

        function decisionCell(row) {{
            return row.accepted
                ? "<span class='accepted'>zaakceptowano</span>"
                : "<span class='rejected'>odrzucono</span>";
        }}

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
                <td>${{row.best_distance}}</td>
                <td>${{row.temperature.toFixed(4)}}</td>
            `;
            body.appendChild(tr);
            restorePageScroll(scrollX, scrollY);
        }}

        function clearSteps() {{
            inserted.clear();
            body.innerHTML = "<tr class='empty-row'><td colspan='7'>Uruchom animację albo przesuń suwak, aby dodawać kroki.</td></tr>";
        }}

        clearButton.addEventListener("click", clearSteps);
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
    </script>
</body>
</html>
"""


def _route_trace(instance: TspInstance, route: list[int]) -> go.Scatter:
    cities = list(instance.cities)
    ordered = [cities[index] for index in route] + [cities[route[0]]]
    return go.Scatter(
        x=[city.x for city in ordered],
        y=[city.y for city in ordered],
        mode="lines",
        line={"color": INK, "width": 2.2},
        hoverinfo="skip",
        name="najlepsza trasa",
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
        name="miasta",
    )


def _route_from(row: dict[str, int | float | str | bool | list[int]], key: str) -> list[int]:
    route = row[key]
    if not isinstance(route, list):
        raise ValueError(f"Historia nie zawiera trasy {key}.")
    return route


def _title(instance_name: str, row: dict[str, int | float | str | bool | list[int]]) -> str:
    accepted = "zaakceptowano" if row["accepted"] else "odrzucono"
    return (
        f"{instance_name}: iteracja {row['iteration']} | best={row['best_distance']} | "
        f"current={row['current_distance']} | T={float(row['temperature']):.4f} | "
        f"{row['operator']} ({accepted}, delta={row['delta']})"
    )
