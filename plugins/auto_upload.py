#(©) PythonBotz

import asyncio
import logging

from pyrogram import filters, Client
from pyrogram.types import Message

from bot import Bot
from config import ADMINS, CHECK_CHANNEL, QUALITIES
from helper_func import parse_upload_caption, normalize_title
from database.database import (
    upsert_pending_file, get_pending_group, delete_pending_group, list_pending_groups,
)
from plugins.post_builder import build_and_post

logger = logging.getLogger(__name__)

# One lock per (title, episode) key so two qualities landing at nearly the
# same instant can't both decide the group is "complete" and double-post.
_group_locks: dict = {}


def _lock_for(key: str) -> asyncio.Lock:
    if key not in _group_locks:
        _group_locks[key] = asyncio.Lock()
    return _group_locks[key]


@Bot.on_message(
    filters.chat(CHECK_CHANNEL) if CHECK_CHANNEL else filters.create(lambda _, __, ___: False),
    group=1,
)
async def on_check_channel_file(client: Client, message: Message):
    if not (message.document or message.video):
        return

    caption_text = message.caption.strip() if message.caption else ""
    parsed = parse_upload_caption(caption_text)
    if not parsed:
        logger.info(f"[auto-upload] caption didn't match expected pattern: {caption_text!r}")
        return

    key = f"{parsed['normalized_title']}|{parsed['episode_key']}"
    async with _lock_for(key):
        await upsert_pending_file(
            title=parsed["title"],
            normalized_title=parsed["normalized_title"],
            episode_key=parsed["episode_key"],
            season=parsed["season"],
            episode=parsed["episode"],
            quality=parsed["quality"],
            tag=parsed["tag"],
            chat_id=message.chat.id,
            message_id=message.id,
        )

        group = await get_pending_group(parsed["normalized_title"], parsed["episode_key"])
        have = set((group or {}).get("qualities", {}).keys())

        if not set(QUALITIES).issubset(have):
            return  # still waiting on more qualities

        try:
            await build_and_post(client, group)
        except Exception as e:
            logger.error(f"[auto-upload] post build failed for {key}: {e}", exc_info=True)
            return  # leave the group in place so a retry/manual fix is possible

        await delete_pending_group(parsed["normalized_title"], parsed["episode_key"])
    _group_locks.pop(key, None)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("clearpending"))
async def clear_pending_cmd(client: Client, message: Message):
    """
    /clearpending            -> lists all stuck/partial groups
    /clearpending TITLE SxxExx -> drops one specific group
    """
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        groups = await list_pending_groups()
        if not groups:
            await message.reply("No pending groups.")
            return
        lines = []
        for g in groups:
            have = ", ".join(sorted(g.get("qualities", {}).keys())) or "none"
            lines.append(f"• <b>{g['title']}</b> {g['episode_key']} — have: {have}")
        lines.append("\nUse <code>/clearpending TITLE SxxExx</code> to drop one.")
        await message.reply("\n".join(lines))
        return

    _, title_part, episode_key = args
    normalized = normalize_title(title_part)
    await delete_pending_group(normalized, episode_key.upper())
    await message.reply(f"Cleared pending group for <b>{title_part}</b> {episode_key.upper()}.")
