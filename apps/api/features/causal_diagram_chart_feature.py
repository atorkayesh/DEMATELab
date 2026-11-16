"""
Causal diagram (influence map), ported from `plot_dematel_influence_map` (`dematel_visualization.py:143-302`)
and drawn as the Qt viewer does (`results_viewer_widget.py:981-1018`): crisp total matrix, the analysis
threshold (mean of the matrix when missing), an 8 x 6 figure, `tight_layout()`.

Nodes are green only when relation > 0 (the cause group is relation >= 0; kept from Qt).
"""

import asyncio
from typing import Optional

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from constants.chart_constants import CAUSAL_DIAGRAM_STYLE
from features.analysis_feature import AnalysisFeature, analysis_feature
from models.analysis_request_models import AnalysisRequest
from models.solver_models import SolverOutput
from utils.figure_utils import FigureRenderer, figure_renderer
from utils.influence_map_utils import InfluenceMapGeometry, influence_map_geometry


class CausalDiagramChartFeature:
    """Renders the causal diagram as PNG."""

    def __init__(
        self,
        analysis: Optional[AnalysisFeature] = None,
        geometry: Optional[InfluenceMapGeometry] = None,
        renderer: Optional[FigureRenderer] = None,
    ):
        """
        Create the feature.

        Args:
            analysis: Analysis feature used to recompute the result; defaults to the shared instance
            geometry: Influence map helper; defaults to the shared instance
            renderer: Figure renderer; defaults to the shared instance
        """
        self._analysis = analysis or analysis_feature
        self._geometry = geometry or influence_map_geometry
        self._renderer = renderer or figure_renderer

    async def render(self, request: AnalysisRequest, dpi: int) -> bytes:
        """
        Recompute the analysis and render the diagram in a worker thread.

        Args:
            request: Validated analysis request
            dpi: Output resolution (100 or 300)

        Returns:
            bytes: PNG content
        """
        return await asyncio.to_thread(self.render_sync, request, dpi)

    def render_sync(self, request: AnalysisRequest, dpi: int) -> bytes:
        """
        Recompute the analysis and render the diagram.

        Args:
            request: Validated analysis request
            dpi: Output resolution (100 or 300)

        Returns:
            bytes: PNG content
        """
        figure = self.draw(self._analysis.solve(request))
        return self._renderer.to_png(figure, dpi)

    def draw(self, output: SolverOutput) -> Figure:
        """
        Draw the diagram for one solver output.

        Args:
            output: Solver output

        Returns:
            Figure: The drawn figure
        """
        style = CAUSAL_DIAGRAM_STYLE
        factors = output.factors
        prominence = np.asarray(output.prominence, dtype=float)
        relation = np.asarray(output.relation, dtype=float)
        total = output.crisp_total_matrix
        threshold = output.threshold_value
        if threshold is None:
            threshold = float(np.mean(total))
        threshold = float(threshold)
        self._geometry.validate(factors, prominence, relation, total, threshold)
        positions = self._geometry.positions(factors, prominence, relation)
        edges = self._geometry.edges(factors, total, threshold)

        figure = self._renderer.new_figure()
        ax = figure.add_subplot(111)
        colors = [style["CAUSE_COLOR"] if value > 0 else style["EFFECT_COLOR"] for value in relation]
        ax.scatter(
            prominence,
            relation,
            c=colors,
            s=style["NODE_SIZE"],
            zorder=3,
            edgecolors=style["NODE_EDGE_COLOR"],
            linewidths=style["NODE_EDGE_WIDTH"],
        )
        for factor, x, y in zip(factors, prominence, relation, strict=True):
            ax.text(
                float(x),
                float(y),
                factor,
                fontsize=style["TEXT_SIZE"],
                ha="center",
                va="center",
                zorder=4,
                color=style["TEXT_COLOR"],
                fontweight="bold",
            )
        ax.axhline(0, color="gray", linewidth=1, linestyle="--", zorder=1)
        ax.axvline(float(np.mean(prominence)), color="gray", linewidth=1, linestyle=":", zorder=1)
        ax.set_xlabel(style["X_LABEL"])
        ax.set_ylabel(style["Y_LABEL"])
        ax.margins(style["MARGINS"])
        self._geometry.draw_edges(ax, edges, positions)
        legend = [
            Patch(color=style["CAUSE_COLOR"], label=style["CAUSE_LEGEND"]),
            Patch(color=style["EFFECT_COLOR"], label=style["EFFECT_LEGEND"]),
        ]
        ax.legend(handles=legend, loc="best")
        if style["SHOW_GRID"]:
            ax.grid(True, linestyle=":", alpha=style["GRID_ALPHA"])
        figure.tight_layout()
        return figure


causal_diagram_chart_feature = CausalDiagramChartFeature()
