"""
Figure rendering to PNG bytes.

Charts are built with matplotlib's object-oriented `Figure` API, never `pyplot`, so concurrent requests do
not share global state and nothing has to be closed: a `Figure` that pyplot never registered is freed with
its last reference.
"""

from io import BytesIO
from typing import Tuple

from matplotlib.figure import Figure

from constants.chart_constants import DOWNLOAD_DPI, FIGURE_SIZE


class FigureRenderer:
    """Creates chart figures and saves them as PNG."""

    def __init__(self, figure_size: Tuple[float, float] = FIGURE_SIZE):
        """
        Create the renderer.

        Args:
            figure_size: Figure size in inches (the Qt plot tabs use 8 x 6)
        """
        self._figure_size = figure_size

    def new_figure(self) -> Figure:
        """
        Create an empty figure at matplotlib's default dpi, as the Qt plot tabs do.

        Returns:
            Figure: New figure
        """
        return Figure(figsize=self._figure_size)

    def to_png(self, figure: Figure, dpi: int) -> bytes:
        """
        Save a figure as PNG.

        Downloads (300 dpi) are cropped with `bbox_inches="tight"` like the Qt PNG export; the display size
        (100 dpi) keeps the whole canvas, as the Qt tab shows it.

        Args:
            figure: Figure to save
            dpi: Output resolution

        Returns:
            bytes: PNG file content
        """
        buffer = BytesIO()
        if dpi == DOWNLOAD_DPI:
            figure.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
        else:
            figure.savefig(buffer, format="png", dpi=dpi)
        return buffer.getvalue()


figure_renderer = FigureRenderer()
