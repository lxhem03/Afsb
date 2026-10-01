import asyncio
import sys
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, PORT
from config import FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4
from config import CHANNEL_ID, ADMINS, OWNER_ID
from plugins import web_server
from aiohttp import web
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL1:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL1)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL1)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL1)).invite_link
                self.invitelink1 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning(f"Bot can't Export Invite link from FORCE_SUB_CHANNEL1! Check value: {FORCE_SUB_CHANNEL1}")
                sys.exit()

        if FORCE_SUB_CHANNEL2:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                self.invitelink2 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning(f"Bot can't Export Invite link from FORCE_SUB_CHANNEL2! Check value: {FORCE_SUB_CHANNEL2}")
                sys.exit()

        if FORCE_SUB_CHANNEL3:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL3)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL3)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL3)).invite_link
                self.invitelink3 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning(f"Bot can't Export Invite link from FORCE_SUB_CHANNEL3! Check value: {FORCE_SUB_CHANNEL3}")
                sys.exit()

        if FORCE_SUB_CHANNEL4:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL4)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL4)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL4)).invite_link
                self.invitelink4 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning(f"Bot can't Export Invite link from FORCE_SUB_CHANNEL4! Check value: {FORCE_SUB_CHANNEL4}")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="@PythonBotz file share test")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make sure bot is Admin in DB Channel. Current CHANNEL_ID: {CHANNEL_ID}")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info("Bot Running..!\n\nCreated by \nhttps://t.me/offchats")
        self.username = usr_bot_me.username

        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        try:
            await self.send_message(OWNER_ID, text="<b><blockquote>🤖 Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ ♻️</blockquote></b>")
        except:
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
