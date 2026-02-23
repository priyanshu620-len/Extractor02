"""
from os import getenv


API_ID = int(getenv("API_ID", "34320281"))
API_HASH = getenv("API_HASH", "e55840d9b1ba82ba7748a30e2bbbfc1a")
BOT_TOKEN = getenv("BOT_TOKEN", "8372745246:AAFsqcrX5a8R6dEuPhgvChBvU-EDSzRjddg")
OWNER_ID = int(getenv("OWNER_ID", "8301160173"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "8152589217,6073936818").split()))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://ONeX_db_user:onexvartikuu142062@cluster0.ga3zort.mongodb.net/?appName=Cluster0")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003533149811"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1003533149811"))

"""
#




# --------------M----------------------------------

import os
from os import getenv
# ---------------R---------------------------------
API_ID = int(os.environ.get("API_ID", "34320281"))
# ------------------------------------------------
API_HASH = os.environ.get("API_HASH", "e55840d9b1ba82ba7748a30e2bbbfc1a")
# ----------------D--------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8372745246:AAFsqcrX5a8R6dEuPhgvChBvU-EDSzRjddg")
# -----------------A-------------------------------
BOT_USERNAME = os.environ.get("extractor011_bot")
# ------------------X------------------------------
OWNER_ID = int(os.environ.get("OWNER_ID", "8301160173"))
# ------------------X------------------------------

SUDO_USERS = list(map(int, getenv("SUDO_USERS", "6073936818,8152589217").split()))
# ------------------------------------------------
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003533149811"))
# ------------------------------------------------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://ONeX_db_user:onexvartikuu142062@cluster0.ga3zort.mongodb.net/?appName=Cluster0")
# -----------------------------------------------
PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", "-1003533149811"))

