"""
Influence map geometry, ported from `dematel_visualization.py:53-140`: input checks, node positions, edges
above the threshold (strictly, diagonal skipped), line widths, and arrows.
"""

from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch

from constants.chart_constants import CAUSAL_DIAGRAM_STYLE
from errors.analysis_errors import InvalidAnalysisInputError

Edge = Tuple[str, str, float]


class InfluenceMapGeometry:
    """Positions, edges, and arrows of the causal diagram."""

    def __init__(self, style: Dict = CAUSAL_DIAGRAM_STYLE):
        """
        Create the helper.

        Args:
            style: Causal diagram style (the Qt `DematelPlotStyle` values)
        """
        self._style = style

    def validate(
        self, factors: Sequence[str], prominence: np.ndarray, relation: np.ndarray, total: np.ndarray, threshold: float
    ) -> None:
        """
        Check the plot input as `_validate_plot_input` does.

        Raises:
            InvalidAnalysisInputError: With the Qt message
        """
        size = len(factors)
        if size == 0:
            raise InvalidAnalysisInputError(public_message="Factors cannot be empty.")
        if prominence.shape[0] != size:
            raise InvalidAnalysisInputError(public_message="Prominence length must match number of factors.")
        if relation.shape[0] != size:
            raise InvalidAnalysisInputError(public_message="Relation length must match number of factors.")
        if total.shape != (size, size):
            raise InvalidAnalysisInputError(public_message="Total matrix shape must match number of factors.")
        if not np.isfinite(threshold):
            raise InvalidAnalysisInputError(public_message="Threshold must be a valid finite number.")

    def positions(
        self, factors: Sequence[str], prominence: np.ndarray, relation: np.ndarray
    ) -> Dict[str, Tuple[float, float]]:
        """
        Place each factor at (prominence, relation).

        Returns:
            Dict[str, Tuple[float, float]]: Position per factor name
        """
        return {factor: (float(p), float(r)) for factor, p, r in zip(factors, prominence, relation, strict=True)}

    def edges(self, factors: Sequence[str], total: np.ndarray, threshold: float) -> List[Edge]:
        """
        List the edges whose total relation value is strictly above the threshold, without self loops.

        Returns:
            List[Edge]: (source, target, weight) in row-major order
        """
        found: List[Edge] = []
        for i in range(len(factors)):
            for j in range(len(factors)):
                if i == j:
                    continue
                weight = float(total[i, j])
                if weight > threshold:
                    found.append((factors[i], factors[j], weight))
        return found

    def line_width(self, weights: Sequence[float], weight: float) -> float:
        """
        Scale an edge weight linearly between the minimum and maximum line widths.

        Returns:
            float: Line width (the midpoint when every weight is equal)
        """
        low, high = self._style["LINE_WIDTH_MIN"], self._style["LINE_WIDTH_MAX"]
        w_min, w_max = min(weights), max(weights)
        if np.isclose(w_min, w_max):
            return (low + high) / 2
        return low + (weight - w_min) * (high - low) / (w_max - w_min)

    def draw_edges(self, ax: Axes, edges: List[Edge], positions: Dict[str, Tuple[float, float]]) -> None:
        """
        Draw the edges: single edges slightly curved, mutual edges as two opposite arcs.

        Args:
            ax: Axes to draw on
            edges: Edges above the threshold
            positions: Node positions
        """
        if not edges:
            return
        weights = [weight for _, _, weight in edges]
        pairs: Dict[Tuple[str, ...], List[Edge]] = defaultdict(list)
        for source, target, weight in edges:
            pairs[tuple(sorted([source, target]))].append((source, target, weight))
        one_way, mutual = self._style["ONE_WAY_RAD"], self._style["BIDIRECTIONAL_RAD"]
        for grouped in pairs.values():
            if len(grouped) == 1:
                source, target, weight = grouped[0]
                self._arrow(ax, positions[source], positions[target], one_way, self.line_width(weights, weight))
                continue
            ordered = sorted(grouped, key=lambda edge: (edge[0], edge[1]))
            for edge, rad in ((ordered[0], mutual), (ordered[1], -mutual)):
                self._arrow(ax, positions[edge[0]], positions[edge[1]], rad, self.line_width(weights, edge[2]))
            for extra in ordered[2:]:
                self._arrow(ax, positions[extra[0]], positions[extra[1]], one_way, self.line_width(weights, extra[2]))

    def _arrow(
        self, ax: Axes, start: Tuple[float, float], end: Tuple[float, float], rad: float, line_width: float
    ) -> None:
        """Add one curved arrow (`_add_arrow`)."""
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=self._style["ARROW_MUTATION_SCALE"],
                linewidth=line_width,
                color=self._style["ARROW_COLOR"],
                alpha=self._style["ARROW_ALPHA"],
                connectionstyle=f"arc3,rad={rad}",
                shrinkA=self._style["SHRINK_A"],
                shrinkB=self._style["SHRINK_B"],
                zorder=2,
            )
        )


influence_map_geometry = InfluenceMapGeometry()
