#(©) PythonBotz 




import os
import logging
from logging.handlers import RotatingFileHandler



#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7577614029:AAHF-6AU-wjU49IKTBCmqCZjRtTHSPVVxKw")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "26728872"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "96985c2aaea6c75408528909b7e18879")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002390658665"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "1705634892"))

#Port
PORT = os.environ.get("PORT", "8000")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://telegramguy21:tnkIwvbNkJ5U3fZ7@botsuse.bpgag.mongodb.net/?retryWrites=true&w=majority&appName=Botsuse")
DB_NAME = os.environ.get("DATABASE_NAME", "AG-TNX")

#Time in seconds for message Auto delete, put 0 to never delete
TIME = int(os.environ.get("TIME", "86400"))

#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL1 = int(os.environ.get("FORCE_SUB_CHANNEL1", "-1002169827133"))
#put 0 to disable
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2", "-1002347470858"))#put 0 to disable
FORCE_SUB_CHANNEL3 = int(os.environ.get("FORCE_SUB_CHANNEL3", "0"))#put 0 to disable
FORCE_SUB_CHANNEL4 = int(os.environ.get("FORCE_SUB_CHANNEL4", "0"))#put 0 to disable

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "100"))

#start message
START_MSG = os.environ.get("START_MESSAGE", "𝑰'𝒎 𝑳𝒖𝒇𝒇𝒚!👒 𝑨𝒏𝒅 𝑰'𝒎 𝒈𝒐𝒏𝒏𝒂 𝒇𝒊𝒏𝒅 𝒕𝒉𝒆 𝑶𝒏𝒆 𝑷𝒊𝒆𝒄𝒆 😁... 𝒖𝒉, 𝑰 𝒎𝒆𝒂𝒏 𝒉𝒆𝒍𝒑 𝒚𝒐𝒖 𝒇𝒊𝒏𝒅 𝒂𝒘𝒆𝒔𝒐𝒎𝒆 𝒂𝒏𝒊𝒎𝒆😅! 𝑪𝒉𝒆𝒄𝒌 𝒐𝒖𝒕 <a href='https://t.me/Animes_Guy'>𝗔𝗻𝗶𝗺𝗲𝘀 𝗚𝘂𝘆!!</a> 𝒂𝒏𝒅 𝒄𝒐𝒎𝒆 𝒕𝒐 𝒎𝒆 𝒂𝒈𝒂𝒊𝒏 😉 , 𝑰 𝒘𝒊𝒍𝒍 𝒑𝒓𝒐𝒗𝒊𝒅𝒆 𝒚𝒐𝒖 𝒕𝒉𝒆 𝒈𝒓𝒆𝒂𝒕𝒆𝒔𝒕 𝒔𝒕𝒐𝒓𝒚 𝒆𝒗𝒆𝒓 𝒕𝒐𝒍𝒅 𝒊𝒏 𝒕𝒉𝒆 𝒉𝒊𝒔𝒕𝒐𝒓𝒚 𝒊𝒏 𝒉𝒊𝒈𝒉 𝒒𝒖𝒂𝒍𝒊𝒕𝒚!! 🎖️𝑾𝒉𝒂𝒕 𝒂𝒓𝒆 𝒚𝒐𝒖 𝒘𝒂𝒊𝒕𝒊𝒏𝒈 𝒇𝒐𝒓??")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "1705634892 7465574522").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "Hᴇʟʟᴏ!\n\nTᴏ ʜᴇʟᴘ ᴘʀᴇᴠᴇɴᴛ sᴘᴀᴍ ᴏɴ ᴏᴜʀ ʙᴏᴛs, ᴏɴʟʏ ᴜsᴇʀs ᴡʜᴏ ᴀʀᴇ ᴍᴇᴍʙᴇʀs ᴏғ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴘᴇʀᴍɪᴛᴛᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. Tᴏ ᴀᴄᴄᴇss ʏᴏᴜʀ ғɪʟᴇs, ᴘʟᴇᴀsᴇ ɪᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʟɪsᴛᴇᴅ ʙᴇʟᴏᴡ ᴀɴᴅ ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ!")

# Start & Fsub Pics ----------------------------------- #

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (os.environ.get("PICS", "https://files.catbox.moe/lllex3.jpg https://files.catbox.moe/2yztvd.jpg https://files.catbox.moe/uhv8s5.webp https://files.catbox.moe/2fbp1d.webp https://files.catbox.moe/pponhx.jpg https://files.catbox.moe/yzx835.jpg")).split() #Required

# Start & Fsub Pics ----------------------------------- #

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "𝑰 𝒅𝒐𝒏'𝒕 𝒘𝒐𝒓𝒌 𝒇𝒐𝒓 𝒚𝒐𝒖, 𝒃𝒖𝒅!!"

ADMINS.append(OWNER_ID)
ADMINS.append(1705634892)

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
