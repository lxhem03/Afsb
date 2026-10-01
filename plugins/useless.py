import time
from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import get_readable_time

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def info(client: Bot, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("★ Cʟᴏsᴇ ★", callback_data="close")]])
    
    start_time = time.time()
    temp_msg = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    end_time = time.time()
    
    ping_time = (end_time - start_time) * 1000
   
    now = datetime.now()
    delta = now - client.uptime
    bottime = get_readable_time(delta.seconds)
    
    await temp_msg.edit(
        f"<b>🚀 UPTIME » {bottime}\n\n📡 PING » {ping_time:.2f} ms\n\n<u>👨‍💻 Developer : @The_TGguy</u></b>",
        reply_markup=reply_markup
    )


@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)
