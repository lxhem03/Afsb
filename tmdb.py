"""
TMDB Image Client
==================
Fetches candidate poster/backdrop images from TMDB for the /setanime
"Manual" poster-image picker. AniList only exposes one cover + one banner
per title, so it can't offer real choice — TMDB exposes arrays of posters
and backdrops per show (and per season, for posters), which is what makes
a Manual picker meaningful.

Never raises on failure — callers get an empty result instead.
"""

import re
import logging
import requests

from config import TMDB_API_KEY

logger = logging.getLogger(__name__)

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/original"
_TIMEOUT = 15


def parse_tmdb_id(text: str):
    """Accepts a bare numeric id or a themoviedb.org URL (e.g.
    https://www.themoviedb.org/tv/290019-some-show-slug) and returns the
    integer TMDB id, or None if it couldn't be found."""
    if not text:
        return None
    text = text.strip()
    if text.isdigit():
        return int(text)
    m = re.search(r"themoviedb\.org/tv/(\d+)", text)
    if m:
        return int(m.group(1))
    # Bare "290019-some-slug" form
    m = re.match(r"^(\d+)-", text)
    if m:
        return int(m.group(1))
    return None


def _auth_kwargs(api_key: str):
    # TMDB has two key formats: the classic v3 "API Key" (query param) and
    # the newer v4 "Read Access Token" (a long JWT, used as a Bearer token).
    if api_key and len(api_key) > 100:
        return {"headers": {"Authorization": f"Bearer {api_key}"}}
    return {"params": {"api_key": api_key}}


def get_tv_images(tmdb_id: int, season: int = None, api_key: str = None):
    """Returns {"posters": [urls...], "backdrops": [urls...]}.

    Posters: season-specific ones first (if a season is given and TMDB has
    any), then the show-level posters.
    Backdrops: show-level only — TMDB doesn't keep season-specific
    backdrops, so all seasons share the same backdrop candidates.
    """
    key = api_key or TMDB_API_KEY
    result = {"posters": [], "backdrops": []}
    if not key or not tmdb_id:
        return result

    auth = _auth_kwargs(key)

    try:
        r = requests.get(f"{TMDB_API_URL}/tv/{tmdb_id}/images", timeout=_TIMEOUT, **auth)
        r.raise_for_status()
        data = r.json()
        result["posters"] = [TMDB_IMG_BASE + p["file_path"] for p in data.get("posters", [])]
        result["backdrops"] = [TMDB_IMG_BASE + p["file_path"] for p in data.get("backdrops", [])]
    except Exception as e:
        logger.warning(f"[TMDB] show-level image fetch failed for {tmdb_id}: {e}")

    if season:
        try:
            r = requests.get(
                f"{TMDB_API_URL}/tv/{tmdb_id}/season/{season}/images",
                timeout=_TIMEOUT, **auth,
            )
            r.raise_for_status()
            data = r.json()
            season_posters = [TMDB_IMG_BASE + p["file_path"] for p in data.get("posters", [])]
            if season_posters:
                # Season posters first — they're the relevant ones.
                result["posters"] = season_posters + [
                    p for p in result["posters"] if p not in season_posters
                ]
        except Exception as e:
            logger.warning(f"[TMDB] season-level image fetch failed for {tmdb_id} S{season}: {e}")

    return result
