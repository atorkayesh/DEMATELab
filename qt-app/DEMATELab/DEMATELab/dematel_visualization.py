# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:45:27 2026

@author: Ali
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Patch


@dataclass(slots=True)
class DematelPlotInput:
    factors: list[str]
    prominence: np.ndarray
    relation: np.ndarray
    total_matrix: np.ndarray
    threshold: float


@dataclass(slots=True)
class DematelPlotStyle:
    figsize: tuple[float, float] = (11, 8)
    node_size: int = 900
    node_edge_color: str = "black"
    node_edge_width: float = 0.7
    cause_color: str = "green"
    effect_color: str = "red"
    text_color: str = "white"
    text_size: int = 10
    arrow_color: str = "black"
    arrow_alpha: float = 0.75
    arrow_mutation_scale: int = 22
    line_width_min: float = 0.6
    line_width_max: float = 4.0
    one_way_rad: float = 0.06
    bidirectional_rad: float = 0.20
    shrink_a: int = 18
    shrink_b: int = 18
    show_grid: bool = True
    grid_alpha: float = 0.4
    dpi: int = 500


def _validate_plot_input(data: DematelPlotInput) -> None:
    n = len(data.factors)

    if n == 0:
        raise ValueError("Factors cannot be empty.")

    if data.prominence.shape[0] != n:
        raise ValueError("Prominence length must match number of factors.")

    if data.relation.shape[0] != n:
        raise ValueError("Relation length must match number of factors.")

    if data.total_matrix.shape != (n, n):
        raise ValueError("Total matrix shape must match number of factors.")

    if not np.isfinite(data.threshold):
        raise ValueError("Threshold must be a valid finite number.")


def _build_positions(
    factors: Sequence[str],
    prominence: np.ndarray,
    relation: np.ndarray,
) -> dict[str, tuple[float, float]]:
    return {
        factor: (float(p), float(r))
        for factor, p, r in zip(factors, prominence, relation)
    }


def _build_edges(
    factors: Sequence[str],
    total_matrix: np.ndarray,
    threshold: float,
    include_self_loops: bool = False,
) -> list[tuple[str, str, float]]:
    edges: list[tuple[str, str, float]] = []
    n = len(factors)

    for i in range(n):
        for j in range(n):
            if not include_self_loops and i == j:
                continue

            weight = float(total_matrix[i, j])
            if weight > threshold:
                edges.append((factors[i], factors[j], weight))

    return edges


def _scale_line_widths(
    weights: Sequence[float],
    weight: float,
    lw_min: float,
    lw_max: float,
) -> float:
    w_min = min(weights)
    w_max = max(weights)

    if np.isclose(w_min, w_max):
        return (lw_min + lw_max) / 2

    return lw_min + (weight - w_min) * (lw_max - lw_min) / (w_max - w_min)


def _add_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    rad: float,
    lw: float,
    style: DematelPlotStyle,
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=style.arrow_mutation_scale,
        linewidth=lw,
        color=style.arrow_color,
        alpha=style.arrow_alpha,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=style.shrink_a,
        shrinkB=style.shrink_b,
        zorder=2,
    )
    ax.add_patch(arrow)


def plot_dematel_influence_map(
    data: DematelPlotInput,
    style: DematelPlotStyle | None = None,
    save_path: str | Path | None = None,
    show: bool = True,
    ax=None,
):
    """
    Plot DEMATEL influence map from computed DEMATEL outputs.

    Nodes:
        x-axis = prominence
        y-axis = relation

    Edges:
        total_matrix[i, j] > threshold
    """
    _validate_plot_input(data)
    style = style or DematelPlotStyle()

    positions = _build_positions(data.factors, data.prominence, data.relation)
    edges = _build_edges(data.factors, data.total_matrix, data.threshold)

    if ax is None:
        fig, ax = plt.subplots(figsize=style.figsize)
    else:
        fig = ax.figure
        ax.clear()

    # Node colors
    node_colors = [
        style.cause_color if value > 0 else style.effect_color
        for value in data.relation
    ]

    # Scatter nodes
    ax.scatter(
        data.prominence,
        data.relation,
        c=node_colors,
        s=style.node_size,
        zorder=3,
        edgecolors=style.node_edge_color,
        linewidths=style.node_edge_width,
    )

    # Node labels
    for factor, x, y in zip(data.factors, data.prominence, data.relation):
        ax.text(
            float(x),
            float(y),
            factor,
            fontsize=style.text_size,
            ha="center",
            va="center",
            zorder=4,
            color=style.text_color,
            fontweight="bold",
        )

    # Reference lines
    ax.axhline(0, color="gray", linewidth=1, linestyle="--", zorder=1)
    ax.axvline(float(np.mean(data.prominence)), color="gray", linewidth=1, linestyle=":", zorder=1)

    ax.set_xlabel("Prominence")
    ax.set_ylabel("Relation")
    ax.margins(0.12)

    # Draw edges
    if edges:
        edge_weights = [weight for _, _, weight in edges]

        pair_edges: dict[tuple[str, str], list[tuple[str, str, float]]] = defaultdict(list)
        for source, target, weight in edges:
            pair_edges[tuple(sorted([source, target]))].append((source, target, weight))

        for _, grouped_edges in pair_edges.items():
            if len(grouped_edges) == 1:
                source, target, weight = grouped_edges[0]
                _add_arrow(
                    ax=ax,
                    start=positions[source],
                    end=positions[target],
                    rad=style.one_way_rad,
                    lw=_scale_line_widths(
                        edge_weights,
                        weight,
                        style.line_width_min,
                        style.line_width_max,
                    ),
                    style=style,
                )
            else:
                grouped_edges_sorted = sorted(grouped_edges, key=lambda x: (x[0], x[1]))
                first = grouped_edges_sorted[0]
                second = grouped_edges_sorted[1]

                _add_arrow(
                    ax=ax,
                    start=positions[first[0]],
                    end=positions[first[1]],
                    rad=style.bidirectional_rad,
                    lw=_scale_line_widths(
                        edge_weights,
                        first[2],
                        style.line_width_min,
                        style.line_width_max,
                    ),
                    style=style,
                )
                _add_arrow(
                    ax=ax,
                    start=positions[second[0]],
                    end=positions[second[1]],
                    rad=-style.bidirectional_rad,
                    lw=_scale_line_widths(
                        edge_weights,
                        second[2],
                        style.line_width_min,
                        style.line_width_max,
                    ),
                    style=style,
                )

                # If somehow more than 2 exist in the same unordered pair, draw the rest normally
                for extra in grouped_edges_sorted[2:]:
                    _add_arrow(
                        ax=ax,
                        start=positions[extra[0]],
                        end=positions[extra[1]],
                        rad=style.one_way_rad,
                        lw=_scale_line_widths(
                            edge_weights,
                            extra[2],
                            style.line_width_min,
                            style.line_width_max,
                        ),
                        style=style,
                    )

    legend_items = [
        Patch(color=style.cause_color, label="Cause factor"),
        Patch(color=style.effect_color, label="Effect factor"),
    ]
    ax.legend(handles=legend_items, loc="best")

    if style.show_grid:
        ax.grid(True, linestyle=":", alpha=style.grid_alpha)

    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=style.dpi, bbox_inches="tight")

    if show and ax is None:
        plt.show()

    return fig, ax
