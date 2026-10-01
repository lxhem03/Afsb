"""
AniList Direct Client
======================
Fetches anime/manga data straight from the AniList GraphQL API.
No worker in the middle.

Features:
  - In-memory TTL cache (1 hour) so repeated queries skip the network
  - Exponential backoff retry (3 attempts) on rate-limits and transient errors
  - Handles 429 Retry-After header
  - Returns None on failure — never raises
"""

import re
import time
import logging
import requests

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
ANILIST_API_URL = "https://graphql.anilist.co"

MEDIA_QUERY = """
query ($id: Int, $search: String, $type: MediaType) {
  Media (id: $id, search: $search, type: $type, sort: SEARCH_MATCH) {
    id
    title {
      romaji
      english
      native
    }
    description
    type
    format
    episodes
    chapters
    volumes
    averageScore
    status
    season
    seasonYear
    studios(isMain: true) {
      nodes {
        name
      }
    }
    coverImage {
      extraLarge
      color
    }
    bannerImage
    genres
    rankings {
      rank
      type
      allTime
      context
    }
    characters(role: MAIN, perPage: 4, sort: FAVOURITES_DESC) {
      edges {
        node {
          name { full }
          image { large medium }
          description
        }
        role
      }
    }
    supportingCharacters: characters(role: SUPPORTING, perPage: 4, sort: FAVOURITES_DESC) {
      edges {
        node {
          name { full }
          image { large medium }
        }
      }
    }
  }
}
"""

# ── In-memory cache ──────────────────────────────────────────────────────────
_CACHE: dict = {}       # { key: (data, expires_at) }
_CACHE_TTL = 3600       # 1 hour

# ── Retry settings ───────────────────────────────────────────────────────────
_MAX_RETRIES = 3
_BASE_BACKOFF = 1.5     # seconds; doubles each attempt: 1.5 → 3 → 6
_TIMEOUT = 20


# ── Helpers ──────────────────────────────────────────────────────────────────

def _cache_key(query: str, media_type: str) -> str:
    return f"anilist:{media_type.upper()}:{query.strip().lower()}"


def _get_cached(key: str):
    entry = _CACHE.get(key)
    if entry and time.time() < entry[1]:
        logger.debug(f"[AniList] Cache HIT: {key}")
        return entry[0]
    if entry:
        del _CACHE[key]
    return None


def _set_cached(key: str, data: dict):
    _CACHE[key] = (data, time.time() + _CACHE_TTL)


def _clean_description(desc: str) -> str:
    if not desc:
        return ""
    desc = re.sub(r"<br\s*/?>", "\n", desc)
    desc = re.sub(r"<[^>]+>", "", desc)
    return desc.strip()


def _build_variables(query: str, media_type: str) -> dict:
    variables: dict = {"type": media_type.upper()}
    if re.fullmatch(r"\d+", query.strip()):
        variables["id"] = int(query.strip())
    elif "anilist.co" in query:
        m = re.search(r"anilist\.co/(?:anime|manga)/(\d+)", query)
        if m:
            variables["id"] = int(m.group(1))
        else:
            variables["search"] = query
    else:
        variables["search"] = query
    return variables


def _process_data(media: dict) -> dict:
    if media.get("description"):
        media["description"] = _clean_description(media["description"])
    return media


# ── Public API ───────────────────────────────────────────────────────────────

def get_anime_data(query: str, media_type: str = "ANIME", id=None):
    """
    Fetch media data directly from AniList GraphQL.

    Args:
        query     : Title or AniList URL to search for.
        media_type: 'ANIME' or 'MANGA'.
        id        : AniList numeric ID — overrides query when given.

    Returns:
        Parsed data dict, or None on failure / not found.
    """
    effective_query = str(id) if id is not None else query
    key = _cache_key(effective_query, media_type)

    cached = _get_cached(key)
    if cached is not None:
        return cached

    variables = _build_variables(effective_query, media_type)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"query": MEDIA_QUERY, "variables": variables}

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = requests.post(
                ANILIST_API_URL,
                json=payload,
                headers=headers,
                timeout=_TIMEOUT,
            )

            # ── Rate limited ───────────────────────────────────────────────
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else _BASE_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    f"[AniList] 429 rate-limited. Waiting {wait:.1f}s "
                    f"(attempt {attempt}/{_MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            # ── Transient server errors ────────────────────────────────────
            if resp.status_code in (500, 502, 503, 504):
                wait = _BASE_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    f"[AniList] HTTP {resp.status_code} on attempt "
                    f"{attempt}/{_MAX_RETRIES}. Retrying in {wait:.1f}s..."
                )
                time.sleep(wait)
                continue

            if not resp.ok:
                logger.warning(f"[AniList] Non-retryable HTTP {resp.status_code} for '{effective_query}'")
                return None

            json_data = resp.json()
            media = json_data.get("data", {}).get("Media")
            if not media:
                logger.info(f"[AniList] No results for '{effective_query}'")
                return None

            data = _process_data(media)
            _set_cached(key, data)
            return data

        except requests.exceptions.Timeout:
            wait = _BASE_BACKOFF * (2 ** (attempt - 1))
            logger.warning(f"[AniList] Timeout on attempt {attempt}/{_MAX_RETRIES}. Retry in {wait:.1f}s...")
            time.sleep(wait)

        except requests.exceptions.ConnectionError as e:
            wait = _BASE_BACKOFF * (2 ** (attempt - 1))
            logger.warning(f"[AniList] Connection error on attempt {attempt}/{_MAX_RETRIES}: {e}. Retry in {wait:.1f}s...")
            time.sleep(wait)

        except Exception as e:
            logger.error(f"[AniList] Unexpected error: {e}", exc_info=True)
            return None

    logger.error(f"[AniList] All {_MAX_RETRIES} attempts failed for '{effective_query}'")
    return None


def clean_description(desc: str) -> str:
    return _clean_description(desc)
