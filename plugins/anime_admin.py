#(©) PythonBotz

from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import ADMINS
from helper_func import normalize_title
from database.database import list_anime_mappings, get_anime_mapping, delete_anime_mapping


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command(["myanime", "listanime"]))
async def list_anime_cmd(client: Client, message: Message):
    mappings = await list_anime_mappings()
    if not mappings:
        await message.reply("No anime mapped yet. Use /setanime to add one.")
        return

    buttons = []
    for m in mappings[:50]:
        has_poster = " 🖼" if m.get("poster_file_id") else ""
        label = f"{m['title']} (AniList {m['anilist_id']}){has_poster}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"anidel_{m['_id']}")])

    more_note = f"\n\n(showing first 50 of {len(mappings)})" if len(mappings) > 50 else ""
    await message.reply(
        f"<b>{len(mappings)} anime mapped.</b> Tap one to delete it.{more_note}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@Bot.on_callback_query(filters.regex(r"^anidel_"), group=-1)
async def delete_anime_cb(client: Client, query: CallbackQuery):
    if query.from_user.id not in ADMINS:
        await query.answer("Admins only.", show_alert=True)
        return
    normalized = query.data.split("anidel_", 1)[1]
    mapping = await get_anime_mapping(normalized)
    await delete_anime_mapping(normalized)
    await query.answer("Deleted.")
    name = mapping["title"] if mapping else normalized
    await query.message.edit(f"Removed mapping for <b>{name}</b>.")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("delanime"))
async def delete_anime_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Usage: <code>/delanime TITLE</code>")
        return
    normalized = normalize_title(args[1])
    mapping = await get_anime_mapping(normalized)
    if not mapping:
        await message.reply("No mapping found for that title.")
        return
    await delete_anime_mapping(normalized)
    await message.reply(f"Removed mapping for <b>{mapping['title']}</b>.")
