"""
from os import getenv


API_ID = int(getenv("API_ID", "34320281"))
API_HASH = getenv("API_HASH", "e55840d9b1ba82ba7748a30e2bbbfc1a")
BOT_TOKEN = getenv("BOT_TOKEN", "")
OWNER_ID = int(getenv("OWNER_ID", "8301160173"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "8152589217,6073936818").split(",")))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://ONeX_db_user:onexvartikuu142062@cluster0.ga3zort.mongodb.net/?appName=Cluster0")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003533149811"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1003533149811"))

"""
#




# --------------M----------------------------------

import os
from os import getenv

# Basic Bot Configs
API_ID = int(getenv("API_ID", "34320281"))
API_HASH = getenv("API_HASH", "e55840d9b1ba82ba7748a30e2bbbfc1a")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# IDs & Database
OWNER_ID = int(getenv("OWNER_ID", "8301160173"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "8152589217,6073936818").split(",")))
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://ONeX_db_user:onexvartikuu142062@cluster0.ga3zort.mongodb.net/?appName=Cluster0")

# Logs & Channels
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003533149811"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1003533149811"))

# --- YEH VARIABLE MISSING THA ---
# Aapka Telegram Channel Link jahan report mein 'Join Us' dikhega
join = getenv("JOIN_URL", "https://t.me/+u9LKPzpFRgtkN2E9") 

# Bot Username
BOT_USERNAME = getenv("BOT_USERNAME", "")

# Thumbnail URL (Optional)
THUMB_URL = getenv("THUMB_URL", "https://telegra.ph/file/your_thumb_id.jpg")
