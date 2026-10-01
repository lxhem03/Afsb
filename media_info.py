"""
Audio / subtitle track language detection for auto-upload captions.

Since all qualities of an episode come from the same source encode, we
only need to read track languages once per episode group — this module
streams just the first MEDIAINFO_SAMPLE_MB of ONE file (track metadata in
a properly-muxed MKV sits near the start) and reads it with ffprobe,
rather than downloading the whole file.

Requires ffmpeg (for ffprobe) to be installed — see Dockerfile.
Never raises: returns ([], []) on any failure so a bad sample never blocks
an auto-post.
"""

import os
import json
import asyncio
import logging
import tempfile

from config import MEDIAINFO_SAMPLE_MB

logger = logging.getLogger(__name__)


async def _download_sample(client, message, max_mb: int) -> str:
    limit_bytes = max_mb * 1024 * 1024
    fd, path = tempfile.mkstemp(suffix=".sample")
    os.close(fd)
    downloaded = 0
    with open(path, "wb") as f:
        async for chunk in client.stream_media(message, limit=0):
            f.write(chunk)
            downloaded += len(chunk)
            if downloaded >= limit_bytes:
                break
    return path


async def get_audio_sub_languages(client, message, max_mb: int = None):
    """Returns (audio_lang_codes, subtitle_lang_codes) as lists of ISO-ish
    3-letter codes (e.g. "eng", "jpn"), possibly with duplicates removed
    by the caller. Returns ([], []) if detection fails for any reason."""
    path = None
    try:
        path = await _download_sample(client, message, max_mb or MEDIAINFO_SAMPLE_MB)

        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-print_format", "json", "-show_streams", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.warning(f"[media_info] ffprobe exited {proc.returncode}: {stderr.decode(errors='ignore')[:300]}")
            return [], []

        data = json.loads(stdout or b"{}")
        audio_langs, sub_langs = [], []
        for stream in data.get("streams", []):
            lang = (stream.get("tags", {}) or {}).get("language", "und")
            codec_type = stream.get("codec_type")
            if codec_type == "audio":
                audio_langs.append(lang)
            elif codec_type == "subtitle":
                sub_langs.append(lang)
        return audio_langs, sub_langs

    except FileNotFoundError:
        logger.error("[media_info] ffprobe not found — is ffmpeg installed?")
        return [], []
    except Exception as e:
        logger.warning(f"[media_info] sample/parse failed: {e}")
        return [], []
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
