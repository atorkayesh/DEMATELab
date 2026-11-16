"""
Chart styling, copied from the Qt app.

`CAUSAL_DIAGRAM_STYLE` holds the `DematelPlotStyle` defaults (`dematel_visualization.py:29-50`) with the
GUI's figure size override (`results_viewer_widget.py:1010`). Heatmap settings follow
`results_viewer_widget.py:1052-1123`. Every chart is drawn on an 8x6 figure at matplotlib's default
dpi and saved at the requested dpi (100 on screen, 300 for downloads, as the Qt PNG export).
"""

from enum import IntEnum
from typing import Tuple

FONT_FAMILY: Tuple[str, ...] = ("Inter", "DejaVu Sans")

PNG_MEDIA_TYPE = "image/png"


class ChartDpi(IntEnum):
    """Accepted chart resolutions: 100 as shown on screen, 300 for downloads."""

    DISPLAY = 100
    DOWNLOAD = 300


DISPLAY_DPI = ChartDpi.DISPLAY
DOWNLOAD_DPI = ChartDpi.DOWNLOAD

FIGURE_SIZE: Tuple[float, float] = (8, 6)

CAUSAL_DIAGRAM_STYLE = {
    "NODE_SIZE": 900,
    "NODE_EDGE_COLOR": "black",
    "NODE_EDGE_WIDTH": 0.7,
    "CAUSE_COLOR": "green",
    "EFFECT_COLOR": "red",
    "TEXT_COLOR": "white",
    "TEXT_SIZE": 10,
    "ARROW_COLOR": "black",
    "ARROW_ALPHA": 0.75,
    "ARROW_MUTATION_SCALE": 22,
    "LINE_WIDTH_MIN": 0.6,
    "LINE_WIDTH_MAX": 4.0,
    "ONE_WAY_RAD": 0.06,
    "BIDIRECTIONAL_RAD": 0.20,
    "SHRINK_A": 18,
    "SHRINK_B": 18,
    "SHOW_GRID": True,
    "GRID_ALPHA": 0.4,
    "MARGINS": 0.12,
    "X_LABEL": "Prominence",
    "Y_LABEL": "Relation",
    "CAUSE_LEGEND": "Cause factor",
    "EFFECT_LEGEND": "Effect factor",
}

HEATMAP_STYLE = {
    "STANDARD_TITLE": "Total Relation Matrix Heatmap",
    "CLUSTER_TITLE": "Cluster-Based Heatmap",
    "COLORBAR_LABEL": "Relation Strength",
    "TITLE_FONT_FAMILY": "Inter",
    "TITLE_FONT_SIZE": 10,
    "TITLE_FONT_WEIGHT": "normal",
    "TITLE_COLOR": "#2d4d4c",
    "TICK_ROTATION": 45,
    "TICK_HA": "right",
}
