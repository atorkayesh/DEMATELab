"""
Total relation matrix heatmaps, from the Qt heatmap tab (`results_viewer_widget.py:1052-1123`).

Standard mode: `imshow` with the default colormap and a "Relation Strength" colourbar. Cluster mode: the
cluster codes (0 = diagonal "No influence", 1-4 = Low … High) with discrete colours. Both use an 8 x 6
figure, factor ticks rotated 45° and `tight_layout()`.
"""

import asyncio
from enum import Enum
from typing import Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.figure import Figure

from constants.chart_constants import HEATMAP_STYLE
from constants.cluster_constants import CLUSTER_COLORS, CLUSTER_NAMES
from constants.linguistic_constants import NO_INFLUENCE_LABEL
from features.analysis_feature import AnalysisFeature, analysis_feature
from features.clustering_feature import ClusteringFeature, clustering_feature
from models.analysis_request_models import AnalysisRequest
from models.solver_models import SolverOutput
from utils.figure_utils import FigureRenderer, figure_renderer


class HeatmapMode(str, Enum):
    """Heatmap variants."""

    STANDARD = "standard"
    CLUSTER = "cluster"


class HeatmapChartFeature:
    """Renders the standard or cluster heatmap as PNG."""

    def __init__(
        self,
        analysis: Optional[AnalysisFeature] = None,
        clustering: Optional[ClusteringFeature] = None,
        renderer: Optional[FigureRenderer] = None,
    ):
        """
        Create the feature.

        Args:
            analysis: Analysis feature used to recompute the result; defaults to the shared instance
            clustering: Clustering feature; defaults to the shared instance
            renderer: Figure renderer; defaults to the shared instance
        """
        self._analysis = analysis or analysis_feature
        self._clustering = clustering or clustering_feature
        self._renderer = renderer or figure_renderer

    async def render(self, request: AnalysisRequest, mode: HeatmapMode, dpi: int) -> bytes:
        """
        Recompute the analysis and render the heatmap in a worker thread.

        Args:
            request: Validated analysis request
            mode: Standard or cluster heatmap
            dpi: Output resolution (100 or 300)

        Returns:
            bytes: PNG content

        Raises:
            ClusteringFailedError: In cluster mode when clustering fails (Qt's message; no fallback)
        """
        return await asyncio.to_thread(self.render_sync, request, mode, dpi)

    def render_sync(self, request: AnalysisRequest, mode: HeatmapMode, dpi: int) -> bytes:
        """
        Recompute the analysis and render the heatmap.

        Args:
            request: Validated analysis request
            mode: Standard or cluster heatmap
            dpi: Output resolution (100 or 300)

        Returns:
            bytes: PNG content
        """
        return self._renderer.to_png(self.draw(self._analysis.solve(request), mode), dpi)

    def draw(self, output: SolverOutput, mode: HeatmapMode) -> Figure:
        """
        Draw the heatmap for one solver output.

        Args:
            output: Solver output
            mode: Standard or cluster heatmap

        Returns:
            Figure: The drawn figure
        """
        matrix = output.crisp_total_matrix
        factors = output.factors
        clusters = self._clustering.cluster(matrix, factors) if mode == HeatmapMode.CLUSTER else None
        figure = self._renderer.new_figure()
        ax = figure.add_subplot(111)
        if clusters is not None:
            # Colour by the ranked label, not the raw KMeans id, so each cell matches its colourbar label.
            legend = [NO_INFLUENCE_LABEL, *CLUSTER_NAMES]
            codes = np.vectorize(legend.index, otypes=[int])(clusters.labels_named)
            cmap = ListedColormap(CLUSTER_COLORS)
            norm = BoundaryNorm(np.arange(-0.5, 5.5, 1), cmap.N)
            image = ax.imshow(codes, cmap=cmap, norm=norm, aspect="auto")
            self._title(ax, HEATMAP_STYLE["CLUSTER_TITLE"])
            colorbar = figure.colorbar(image, ax=ax, ticks=np.arange(len(legend)))
            colorbar.set_ticklabels(legend)
        else:
            image = ax.imshow(matrix)
            self._title(ax, HEATMAP_STYLE["STANDARD_TITLE"])
            colorbar = figure.colorbar(image, ax=ax)
            colorbar.set_label(HEATMAP_STYLE["COLORBAR_LABEL"])
        ax.set_xticks(range(len(factors)))
        ax.set_yticks(range(len(factors)))
        ax.set_xticklabels(factors, rotation=HEATMAP_STYLE["TICK_ROTATION"], ha=HEATMAP_STYLE["TICK_HA"])
        ax.set_yticklabels(factors)
        figure.tight_layout()
        return figure

    def _title(self, ax: Axes, text: str) -> None:
        """Set a heatmap title in the Qt style."""
        ax.set_title(
            text,
            fontfamily=HEATMAP_STYLE["TITLE_FONT_FAMILY"],
            fontsize=HEATMAP_STYLE["TITLE_FONT_SIZE"],
            fontweight=HEATMAP_STYLE["TITLE_FONT_WEIGHT"],
            color=HEATMAP_STYLE["TITLE_COLOR"],
        )


heatmap_chart_feature = HeatmapChartFeature()
