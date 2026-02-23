"""
from os import getenv


API_ID = int(getenv("API_ID", "26003553"))
API_HASH = getenv("API_HASH", "c1f27c622acecf9bf6e71d0d295e75f9")
BOT_TOKEN = getenv("BOT_TOKEN", "8172684751:AAFrKOePs4i_8Zbo3OciESAnP40EVT9cQlQ")
OWNER_ID = int(getenv("OWNER_ID", "8152589217"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "8152589217,6073936818").split()))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://MRDAXX:MRDAXX@mrdaxx.prky3aj.mongodb.net/?retryWrites=true&w=majority")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002656120306"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1002630993737"))

"""
#




# --------------M----------------------------------

import os
from os import getenv
# ---------------R---------------------------------
API_ID = int(os.environ.get("API_ID", "26003553"))
# ------------------------------------------------
API_HASH = os.environ.get("API_HASH", "c1f27c622acecf9bf6e71d0d295e75f9")
# ----------------D--------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8172684751:AAFrKOePs4i_8Zbo3OciESAnP40EVT9cQlQ")
# -----------------A-------------------------------
BOT_USERNAME = os.environ.get("Nooneknowswhoknows_bot")
# ------------------X------------------------------
OWNER_ID = int(os.environ.get("OWNER_ID", "8152589217"))
# ------------------X------------------------------

SUDO_USERS = list(map(int, getenv("SUDO_USERS", "8152589217,6073936818").split()))
# ------------------------------------------------
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002656120306"))
# ------------------------------------------------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://jaydevswebpannel:jaydevgadhvi@core.efzs6h3.mongodb.net/?retryWrites=true&w=majority&appName=Core")
# -----------------------------------------------
PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", "-1002630993737"))

