from __future__ import annotations
import io, zipfile
from pathlib import Path
import urllib.request

_RELEASE_URL = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"

_NEEDED = [
    "Inter-Thin.ttf",
    "Inter-ExtraLight.ttf",
    "Inter-Light.ttf",
    "Inter-Regular.ttf",
    "Inter-Medium.ttf",
    "Inter-SemiBold.ttf",
    "Inter-Bold.ttf",
    "Inter-ExtraBold.ttf",
    "Inter-Black.ttf",
]


def ensure_inter_fonts(assets_dir: Path) -> list[str]:
    """Return absolute font paths, downloading from GitHub if missing."""
    font_dir = assets_dir / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)

    sentinel = font_dir / "Inter-Regular.ttf"
    if not sentinel.exists():
        _download_fonts(font_dir)

    return [str(font_dir / name) for name in _NEEDED if (font_dir / name).exists()]


def _download_fonts(font_dir: Path) -> None:
    try:
        data = urllib.request.urlopen(_RELEASE_URL, timeout=15).read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for member in zf.namelist():
                filename = Path(member).name
                if filename in _NEEDED:
                    (font_dir / filename).write_bytes(zf.read(member))
    except Exception:
        pass
