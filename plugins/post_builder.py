"""
Turns a completed pending-group (all QUALITIES present) into a finished
auto-post: copies the files into the DB channel back-to-back (so the
existing /batch-style link format works unmodified), fetches AniList
data, detects audio/subtitle languages, builds the caption, and sends it
with the saved/AniList poster to DEST_CHANNEL.
"""

import asyncio
import logging

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait

from config import CHANNEL_ID, DEST_CHANNEL, QUALITIES
from helper_func import encode
from anilist import get_anime_data
from database.database import get_anime_mapping
from media_info import get_audio_sub_languages
from caption_format import build_caption

logger = logging.getLogger(__name__)

DOWNLOAD_BUTTON_TEXT = "‎✨ 𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍 ✨"


async def _copy_with_retry(client, **kwargs):
    try:
        return await client.copy_message(**kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await client.copy_message(**kwargs)


async def build_and_post(client, group: dict):
    title = group["title"]
    normalized_title = group["normalized_title"]
    quality_info = group.get("qualities", {})

    mapping = await get_anime_mapping(normalized_title)
    anilist_id = mapping.get("anilist_id") if mapping else None

    # AniList lookup is a sync requests call — keep it off the event loop.
    al_data = await asyncio.to_thread(get_anime_data, str(anilist_id) if anilist_id else title)

    # 1) Copy the four quality files into the DB channel, in fixed order,
    #    back-to-back, so the resulting message IDs are contiguous and the
    #    existing get-{first}-{last} batch-link format just works.
    copied_messages = []
    for quality in QUALITIES:
        info = quality_info.get(quality)
        if not info:
            logger.error(f"[post_builder] missing quality {quality} for {normalized_title} {group.get('episode_key')} — aborting")
            return
        copied = await _copy_with_retry(
            client,
            chat_id=CHANNEL_ID,
            from_chat_id=info["chat_id"],
            message_id=info["message_id"],
            disable_notification=True,
        )
        copied_messages.append(copied)
        await asyncio.sleep(1)  # be gentle on flood limits between copies

    first_id = copied_messages[0].id
    last_id = copied_messages[-1].id
    converted_first = first_id * abs(client.db_channel.id)
    converted_last = last_id * abs(client.db_channel.id)
    base64_string = await encode(f"get-{converted_first}-{converted_last}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    # 2) Detect audio/subtitle languages from just one of the copied files
    #    (all qualities share the same source encode).
    try:
        audio_langs, sub_langs = await get_audio_sub_languages(client, copied_messages[0])
    except Exception as e:
        logger.warning(f"[post_builder] language detection failed: {e}")
        audio_langs, sub_langs = [], []

    caption_html = build_caption(al_data, group, audio_langs, sub_langs)

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(DOWNLOAD_BUTTON_TEXT, url=link)]]
    )

    # 3) Pick the image: saved poster file_id > a freshly rendered one was
    #    never generated here (that only happens in /setanime) > raw
    #    AniList cover as a last resort > text-only post.
    poster_file_id = mapping.get("poster_file_id") if mapping else None
    cover_url = None
    if al_data:
        cover_url = (al_data.get("coverImage") or {}).get("extraLarge")

    if poster_file_id:
        await client.send_photo(
            DEST_CHANNEL, photo=poster_file_id,
            caption=caption_html, parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    elif cover_url:
        await client.send_photo(
            DEST_CHANNEL, photo=cover_url,
            caption=caption_html, parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    else:
        await client.send_message(
            DEST_CHANNEL, caption_html, parse_mode=ParseMode.HTML,
            reply_markup=reply_markup, disable_web_page_preview=True,
        )
