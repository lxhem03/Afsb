#(©) PythonBotz

import os
import logging
from logging.handlers import RotatingFileHandler


# ──────────────────────────────────────────────────────────────────────────
# Core Telegram / Mongo credentials — FILL THESE IN (env vars recommended,
# the "" / 0 defaults below are intentionally blank)
# ──────────────────────────────────────────────────────────────────────────

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8147541001:AAEx7i9frhH1WwXtYnip5TtBgjInN9y4HyM")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "39545686"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "0ed4ebf411d1dc0fc63b821a08ad889b")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003995716704"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "7465574522"))

#Port
PORT = os.environ.get("PORT", "8000")

#Database
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://itzmikeyhere21:oa9L3ts4reFl3uWH@demonstration.a1im111.mongodb.net/?appName=demonstration")
DB_NAME = os.environ.get("DATABASE_NAME", "Atwork")

#Time in seconds for message Auto delete, put 0 to never delete
TIME = int(os.environ.get("TIME", "86400"))

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL1 = int(os.environ.get("FORCE_SUB_CHANNEL1", "0"))#put 0 to disable
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2", "0"))#put 0 to disable
FORCE_SUB_CHANNEL3 = int(os.environ.get("FORCE_SUB_CHANNEL3", "0"))#put 0 to disable
FORCE_SUB_CHANNEL4 = int(os.environ.get("FORCE_SUB_CHANNEL4", "0"))#put 0 to disable

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "100"))

#start message
START_MSG = os.environ.get("START_MESSAGE", "𝑰'𝒎 𝑳𝒖𝒇𝒇𝒚!👒 𝑨𝒏𝒅 𝑰'𝒎 𝒈𝒐𝒏𝒏𝒂 𝒇𝒊𝒏𝒅 𝒕𝒉𝒆 𝑶𝒏𝒆 𝑷𝒊𝒆𝒄𝒆 😁... 𝒖𝒉, 𝑰 𝒎𝒆𝒂𝒏 𝒉𝒆𝒍𝒑 𝒚𝒐𝒖 𝒇𝒊𝒏𝒅 𝒂𝒘𝒆𝒔𝒐𝒎𝒆 𝒂𝒏𝒊𝒎𝒆😅! 𝑪𝒉𝒆𝒄𝒌 𝒐𝒖𝒕 <a href='https://t.me/Animes_Guy'>𝗔𝗻𝗶𝗺𝗲𝘀 𝗚𝘂𝘆!!</a> 𝒂𝒏𝒅 𝒄𝒐𝒎𝒆 𝒕𝒐 𝒎𝒆 𝒂𝒈𝒂𝒊𝒏 😉 , 𝑰 𝒘𝒊𝒍𝒍 𝒑𝒓𝒐𝒗𝒊𝒅𝒆 𝒚𝒐𝒖 𝒕𝒉𝒆 𝒈𝒓𝒆𝒂𝒕𝒆𝒔𝒕 𝒔𝒕𝒐𝒓𝒚 𝒆𝒗𝒆𝒓 𝒕𝒐𝒍𝒅 𝒊𝒏 𝒕𝒉𝒆 𝒉𝒊𝒔𝒕𝒐𝒓𝒚 𝒊𝒏 𝒉𝒊𝒈𝒉 𝒒𝒖𝒂𝒍𝒊𝒕𝒚!! 🎖️𝑾𝒉𝒂𝒕 𝒂𝒓𝒆 𝒚𝒐𝒖 𝒘𝒂𝒊𝒕𝒊𝒏𝒈 𝒇𝒐𝒓??")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "7465574522").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "Hᴇʟʟᴏ!\n\nTᴏ ʜᴇʟᴘ ᴘʀᴇᴠᴇɴᴛ sᴘᴀᴍ ᴏɴ ᴏᴜʀ ʙᴏᴛs, ᴏɴʟʏ ᴜsᴇʀs ᴡʜᴏ ᴀʀᴇ ᴍᴇᴍʙᴇʀs ᴏғ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴘᴇʀᴍɪᴛᴛᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. Tᴏ ᴀᴄᴄᴇss ʏᴏᴜʀ ғɪʟᴇs, ᴘʟᴇᴀsᴇ ɪᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʟɪsᴛᴇᴅ ʙᴇʟᴏᴡ ᴀɴᴅ ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ!")

# Start & Fsub Pics ----------------------------------- #

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (os.environ.get("PICS", "https://files.catbox.moe/lllex3.jpg")).split() #Required

# Start & Fsub Pics ----------------------------------- #

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "𝑰 𝒅𝒐𝒏'𝒕 𝒘𝒐𝒓𝒌 𝒇𝒐𝒓 𝒚𝒐𝒖, 𝒃𝒖𝒅!!"

if OWNER_ID:
    ADMINS.append(OWNER_ID)

# ──────────────────────────────────────────────────────────────────────────
# Auto-upload feature (new)
# ──────────────────────────────────────────────────────────────────────────

#Channel your encoder bots upload episodes into. The bot watches this
#channel, groups files by anime + episode, and auto-posts once every
#quality in QUALITIES has arrived. Put 0 to leave auto-upload disabled.
CHECK_CHANNEL = int(os.environ.get("CHECK_CHANNEL", "-1004425570059"))

#Channel the finished, formatted post (poster + caption + download button)
#gets sent to. Put 0 to leave auto-upload disabled.
DEST_CHANNEL = int(os.environ.get("DEST_CHANNEL", "-1004478468518"))

#Qualities a group must have, in this order, before it is auto-posted.
#Edit this list if your encoders use different quality labels.
QUALITIES = os.environ.get("QUALITIES", "360p 480p 720p 1080p").split()

#How long (seconds) a partially-filled quality group is kept before it's
#considered stuck. Doesn't auto-delete anything by itself — use
#/clearpending to drop a stuck group. Default 6 hours.
GROUP_TIMEOUT = int(os.environ.get("GROUP_TIMEOUT", "21600"))

#How many MB to sample from the start of a video file when reading its
#audio/subtitle track languages via ffprobe. Needs ffmpeg installed
#(see Dockerfile).
MEDIAINFO_SAMPLE_MB = int(os.environ.get("MEDIAINFO_SAMPLE_MB", "20"))

# ──────────────────────────────────────────────────────────────────────────
# Poster generation (new) — AniList is free/keyless, TMDB needs a key
# from https://www.themoviedb.org/settings/api
# ──────────────────────────────────────────────────────────────────────────

#TMDB API key (v3 "API Key" or v4 "Read Access Token" both work), used
#only for Manual-mode poster image candidates in /setanime.
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
