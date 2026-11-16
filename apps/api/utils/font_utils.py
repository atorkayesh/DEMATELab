"""
Font registration for the charts.

The charts use Inter, as the Qt app does. The font files ship with the API in `assets/fonts/` and are
registered with matplotlib at startup; nothing is downloaded. DejaVu Sans is the fallback.
"""

from pathlib import Path
from typing import List, Optional

from matplotlib import font_manager, rcParams

from constants.app_constants import PROJECT_PATHS
from constants.chart_constants import FONT_FAMILY


class FontRegistrar:
    """Registers the bundled fonts with matplotlib."""

    def __init__(self, fonts_dir: Optional[Path] = None):
        """
        Create the registrar.

        Args:
            fonts_dir: Folder with the `.ttf` files; defaults to `assets/fonts`
        """
        self._fonts_dir = fonts_dir or PROJECT_PATHS["FONTS_DIR"]

    def register_inter_fonts(self) -> List[str]:
        """
        Register every `.ttf` file in the fonts folder and make Inter the default family.

        Returns:
            List[str]: Paths of the registered font files (empty when the folder has none)
        """
        paths = sorted(str(path) for path in self._fonts_dir.glob("*.ttf"))
        for path in paths:
            font_manager.fontManager.addfont(path)
        rcParams["font.family"] = list(FONT_FAMILY)
        return paths


font_registrar = FontRegistrar()
