"""
Font Manager - Reliable font loader for local fonts directory
Works on Heroku / Docker / local environments
"""

import os
from pathlib import Path

# --------------------------------------------------
# Resolve PROJECT ROOT safely
# --------------------------------------------------
# font.py location → repo root assumed
PROJECT_ROOT = Path(__file__).resolve().parent

# fonts folder is beside font.py
FONT_DIR = PROJECT_ROOT / "fonts"

# Supported font extensions
VALID_EXTS = {".ttf", ".otf", ".woff", ".woff2"}

# normalized name -> Path
_LOCAL_FONTS_MAP: dict[str, Path] = {}


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _normalize(name: str) -> str:
    """Normalize font name for lookup."""
    return name.lower().replace(" ", "-").replace("_", "-")


# --------------------------------------------------
# Initialize fonts
# --------------------------------------------------

def _initialize_fonts():
    _LOCAL_FONTS_MAP.clear()

    if not FONT_DIR.exists():
        print(f"✗ FONT DIR NOT FOUND: {FONT_DIR}")
        return

    for file in FONT_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in VALID_EXTS:
            key = _normalize(file.stem)
            _LOCAL_FONTS_MAP[key] = file

    print(f"✓ Loaded {len(_LOCAL_FONTS_MAP)} fonts from {FONT_DIR}")


_initialize_fonts()


# --------------------------------------------------
# Public API
# --------------------------------------------------

def get_font(name: str) -> str | None:
    """
    Return absolute path of a font.
    """

    key = _normalize(name)
    path = _LOCAL_FONTS_MAP.get(key)

    if path and path.exists():
        return str(path)

    print(f"✗ Font not found: {name} -> {key}")
    return None


def get_fonts() -> dict[str, str]:
    """
    Return all fonts as {normalized_name: absolute_path}
    """
    return {k: str(v) for k, v in _LOCAL_FONTS_MAP.items() if v.exists()}


# --------------------------------------------------
# Recommended loader (NEW)
# --------------------------------------------------

from PIL import ImageFont


def load_font(name: str, size: int):
    """
    Safe font loader for PIL.
    NEVER returns ImageFont.load_default().
    """

    path = get_font(name)

    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception as e:
            print(f"✗ Failed loading font {name}: {e}")

    # hard fallback (must exist in repo)
    fallback = FONT_DIR / "Poppins-Regular.ttf"
    print(f"⚠ Using fallback font: {fallback}")

    return ImageFont.truetype(str(fallback), size)

def load_font_safe(name: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Universal safe font loader.
    NEVER falls back to PIL default bitmap font.
    """

    path = get_font(name)

    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception as e:
            print(f"Font load error ({name}):", e)

    # guaranteed fallback (must exist)
    fallback = get_font("Poppins-Regular")

    if fallback:
        return ImageFont.truetype(fallback, size)

    raise RuntimeError("No usable fonts found.")
    
# --------------------------------------------------
# Debug
# --------------------------------------------------

if __name__ == "__main__":
    print("Project root:", PROJECT_ROOT)
    print("Font dir:", FONT_DIR)
    print("Fonts:", list(get_fonts().keys()))
