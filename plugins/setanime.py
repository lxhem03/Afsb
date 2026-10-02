#(©) PythonBotz

import re
import asyncio
import logging
from io import BytesIO

import requests
from PIL import Image
from pyrogram import filters, Client
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from bot import Bot
from config import ADMINS
from helper_func import normalize_title
from anilist import get_anime_data
from tmdb import get_tv_images, parse_tmdb_id
from poster_gen import generate_poster, TEMPLATES
from database.database import set_anime_mapping, set_anime_poster

logger = logging.getLogger(__name__)

CALLBACK_TIMEOUT = 120
PICKER_TIMEOUT = 180

# One pending callback-wait per chat, so the generic cbb.py callback
# handler doesn't need to know anything about /setanime.
_pending_cb: dict = {}

_SETANIME_ARGS_RE = re.compile(
    r"^(?P<title>.+?)\s*-ani\s+(?P<ani>\d+)"
    r"(?:\s+-tmdb\s+(?P<tmdb>\S+))?"
    r"(?:\s+-s\s+(?P<season>\d+))?\s*$",
    re.IGNORECASE,
)


def _probe_image_orientation(url: str, timeout: int = 15):
    """Downloads a direct image link and reports whether it's landscape or
    portrait, so it can be routed to the right poster slot automatically.
    Returns (is_ok, is_landscape). is_ok is False if the download/decode
    failed (bad link, not an image, etc.)."""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        w, h = img.size
        return True, w >= h
    except Exception as e:
        logger.warning(f"[setanime] couldn't probe direct image link {url!r}: {e}")
        return False, None


async def _wait_for_callback(chat_id: int, timeout: int = CALLBACK_TIMEOUT) -> CallbackQuery:
    fut = asyncio.get_event_loop().create_future()
    _pending_cb[chat_id] = fut
    try:
        return await asyncio.wait_for(fut, timeout)
    finally:
        _pending_cb.pop(chat_id, None)


# Registered in an early group so it gets first look at callbacks for any
# chat currently waiting inside /setanime; harmless everywhere else since
# the filter only matches those chats.
@Bot.on_callback_query(filters.create(lambda _, __, q: q.message.chat.id in _pending_cb), group=-1)
async def _setanime_callback_router(client: Client, query: CallbackQuery):
    fut = _pending_cb.get(query.message.chat.id)
    if fut and not fut.done():
        fut.set_result(query)
    await query.answer()


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("setanime"))
async def setanime_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Usage:\n<code>/setanime TITLE -ani ANILIST_ID [-tmdb TMDB_ID_OR_URL] [-s SEASON]</code>\n\n"
            "Example:\n<code>/setanime One Piece -ani 21</code>",
        )
        return

    match = _SETANIME_ARGS_RE.match(args[1].strip())
    if not match:
        await message.reply("Couldn't parse that. Make sure you included <code>-ani ANILIST_ID</code>.")
        return

    gd = match.groupdict()
    title = gd["title"].strip()
    anilist_id = int(gd["ani"])
    tmdb_id = parse_tmdb_id(gd["tmdb"]) if gd["tmdb"] else None
    season = int(gd["season"]) if gd["season"] else None
    normalized = normalize_title(title)

    await set_anime_mapping(normalized, title, anilist_id, tmdb_id, season)

    summary = f"Saved mapping for <b>{title}</b> → AniList {anilist_id}"
    if tmdb_id:
        summary += f", TMDB {tmdb_id}" + (f" S{season}" if season else "")
    await message.reply(summary + "\n\nNow let's make its poster.")

    # ── Step 1: poster format ────────────────────────────────────────────
    fmt_buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton(label, callback_data=f"setani_fmt_{code}")
        for code, (label, _) in TEMPLATES.items()
    ]])
    step1 = await message.reply("Select poster format:", reply_markup=fmt_buttons)
    try:
        q = await _wait_for_callback(message.chat.id)
    except asyncio.TimeoutError:
        await step1.edit("Timed out. Run /setanime again.")
        return
    fmt = q.data.split("setani_fmt_", 1)[1]
    fmt_label = TEMPLATES[fmt][0]
    await step1.edit(f"Format: <b>{fmt_label}</b>")

    # ── Step 2: Auto or Manual image ────────────────────────────────────
    mode_buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("Auto", callback_data="setani_mode_auto"),
        InlineKeyboardButton("Manual", callback_data="setani_mode_manual"),
    ]])
    step2 = await message.reply("Auto (AniList image) or Manual (pick from TMDB)?", reply_markup=mode_buttons)
    try:
        q = await _wait_for_callback(message.chat.id)
    except asyncio.TimeoutError:
        await step2.edit("Timed out. Run /setanime again.")
        return
    mode = "manual" if q.data == "setani_mode_manual" else "auto"
    await step2.edit(f"Mode: <b>{mode.capitalize()}</b>")

    al_data = await asyncio.to_thread(get_anime_data, str(anilist_id))
    if not al_data:
        await message.reply("Couldn't fetch this anime from AniList — check the id. Aborting.")
        return

    poster_url = (al_data.get("coverImage") or {}).get("extraLarge")
    backdrop_url = al_data.get("bannerImage")

    # ── Manual mode: get a TMDB id if we don't have one, then let the
    #    admin pick an image from the candidates ─────────────────────────
    if mode == "manual":
        direct_image_assigned = False
        if not tmdb_id:
            try:
                reply = await client.ask(
                    chat_id=message.chat.id,
                    text="Manual mode needs an image source. Send a TMDB id/URL, "
                         "a direct image download link, or /skip to fall back to "
                         "Auto (AniList image).",
                    filters=filters.text, timeout=PICKER_TIMEOUT,
                )
            except asyncio.TimeoutError:
                await message.reply("Timed out — falling back to Auto.")
                mode = "auto"
            else:
                text = (reply.text or "").strip()
                looks_like_tmdb = parse_tmdb_id(text) is not None
                if text == "/skip":
                    mode = "auto"
                elif text.lower().startswith(("http://", "https://")) and not looks_like_tmdb:
                    ok, is_landscape = await asyncio.to_thread(_probe_image_orientation, text)
                    if not ok:
                        await reply.reply("Couldn't download that link — falling back to Auto.")
                        mode = "auto"
                    else:
                        if is_landscape:
                            backdrop_url = text
                        else:
                            poster_url = text
                        direct_image_assigned = True
                        await reply.reply(
                            f"Got it — using that as the {'landscape/backdrop' if is_landscape else 'portrait/cover'} image."
                        )
                else:
                    tmdb_id = parse_tmdb_id(text)
                    if not tmdb_id:
                        await reply.reply("Couldn't read a TMDB id from that — falling back to Auto.")
                        mode = "auto"

        if mode == "manual" and not direct_image_assigned:
            images = await asyncio.to_thread(get_tv_images, tmdb_id, season)
            candidates = (images.get("posters") or [])[:8]
            if not candidates:
                await message.reply("No TMDB posters found for that id/season — falling back to Auto.")
                mode = "auto"
            else:
                sent = []
                for idx, url in enumerate(candidates):
                    kb = InlineKeyboardMarkup([[
                        InlineKeyboardButton(f"Use this ({idx + 1})", callback_data=f"setani_pick_{idx}")
                    ]])
                    try:
                        m = await client.send_photo(
                            message.chat.id, url,
                            caption=f"Poster option {idx + 1}/{len(candidates)}",
                            reply_markup=kb,
                        )
                        sent.append(m)
                    except Exception as e:
                        logger.warning(f"[setanime] failed sending TMDB candidate {idx}: {e}")

                try:
                    q = await _wait_for_callback(message.chat.id, timeout=PICKER_TIMEOUT)
                except asyncio.TimeoutError:
                    await message.reply("Timed out picking a poster — falling back to Auto.")
                else:
                    picked_idx = int(q.data.split("setani_pick_", 1)[1])
                    poster_url = candidates[picked_idx]
                    backdrop_candidates = images.get("backdrops") or []
                    if backdrop_candidates:
                        backdrop_url = backdrop_candidates[0]

                for m in sent:
                    try:
                        await m.delete()
                    except Exception:
                        pass

    # ── Render and confirm ───────────────────────────────────────────────
    poster_bytes = await asyncio.to_thread(generate_poster, fmt, al_data, poster_url, backdrop_url)
    if not poster_bytes:
        await message.reply("Poster generation failed. Nothing was saved.")
        return

    confirm_buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("Yes", callback_data="setani_conf_yes"),
        InlineKeyboardButton("No", callback_data="setani_conf_no"),
    ]])
    preview = await message.reply_photo(poster_bytes, caption="Use this poster?", reply_markup=confirm_buttons)

    try:
        q = await _wait_for_callback(message.chat.id)
    except asyncio.TimeoutError:
        await message.reply("Timed out. Run /setanime again.")
        return

    if q.data == "setani_conf_yes":
        file_id = preview.photo.file_id
        await set_anime_poster(normalized, fmt, file_id)
        await preview.edit_caption("Saved ✅ — this poster will be reused for future auto-posts of this anime.")
    else:
        await preview.edit_caption("Discarded. Run /setanime again to restart.")
