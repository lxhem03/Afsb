"""
Poster generation wrapper used by /setanime.

Wraps the three ported templates (AniList-style, Crunchyroll-style,
Netflix-style) behind one call, and lets the caller override which
poster/backdrop image gets drawn — AniList's own image (Auto mode) or a
TMDB image the user picked (Manual mode).
"""

import io
import logging

from PIL import Image

from templates.anilist_poster import create_poster as _anilist_poster
from templates.netflix import create_poster as _netflix_poster
from templates.crunchyroll_poster import generate_poster as _crunchyroll_poster

logger = logging.getLogger(__name__)

# fmt code -> (label, render_fn)
TEMPLATES = {
    "ani": ("AniList", _anilist_poster),
    "crun": ("Crunchyroll", _crunchyroll_poster),
    "net": ("Netflix", _netflix_poster),
}


def _apply_images(al_data: dict, poster_url: str, backdrop_url: str) -> dict:
    """Returns a copy of the AniList data dict with its image fields
    overridden. All three templates read images in slightly different
    ways, so every field that could be read is set:
      - anilist_poster.py reads bannerImage / coverImage.extraLarge
      - crunchyroll_poster.py / netflix.py read images.banner_backdrop /
        images.portrait_poster first, falling back to bannerImage /
        coverImage.extraLarge
    """
    data = dict(al_data or {})
    cover = dict(data.get("coverImage") or {})

    final_poster = poster_url or cover.get("extraLarge")
    final_backdrop = backdrop_url or data.get("bannerImage") or final_poster

    cover["extraLarge"] = final_poster
    data["coverImage"] = cover
    data["bannerImage"] = final_backdrop
    data["images"] = {
        "banner_backdrop": final_backdrop,
        "landscape_poster": final_backdrop,
        "portrait_poster": final_poster,
    }
    return data


def generate_poster(fmt: str, al_data: dict, poster_url: str = None, backdrop_url: str = None):
    """Renders a poster as a JPEG BytesIO, or None on failure/unknown fmt."""
    entry = TEMPLATES.get(fmt)
    if not entry:
        logger.error(f"[poster_gen] unknown format: {fmt}")
        return None
    _, render_fn = entry

    data = _apply_images(al_data, poster_url, backdrop_url)

    try:
        result = render_fn(data)
    except Exception as e:
        logger.error(f"[poster_gen] template '{fmt}' raised: {e}", exc_info=True)
        return None

    # Templates may return a PIL Image or an already-encoded BytesIO.
    if isinstance(result, (bytes, bytearray)):
        result = Image.open(io.BytesIO(result))
    elif isinstance(result, io.BytesIO):
        result.seek(0)
        try:
            result = Image.open(result)
        except Exception:
            result.seek(0)
            return result  # already a usable image buffer

    if not hasattr(result, "save"):
        logger.error(f"[poster_gen] template '{fmt}' returned unusable type: {type(result)}")
        return None

    if result.mode in ("RGBA", "P", "LA"):
        result = result.convert("RGB")

    out = io.BytesIO()
    out.name = "poster.jpg"
    result.save(out, "JPEG", quality=92)
    out.seek(0)
    return out
