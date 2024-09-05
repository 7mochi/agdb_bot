import os

from dotenv import load_dotenv


def read_bool(value: str) -> bool:
    return value.lower() == "true"


load_dotenv()


APP_COMPONENT = os.environ["APP_COMPONENT"]

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_AGDB_GUILD_ID = int(os.environ["DISCORD_AGDB_GUILD_ID"])
DISCORD_ADMIN_ROLE_ID = int(os.environ["DISCORD_ADMIN_ROLE_ID"])
DISCORD_BAN_LOG_CHANNEL_ID = int(os.environ["DISCORD_BAN_LOG_CHANNEL_ID"])

AGDB_API_URL = os.environ["AGDB_API_URL"]
AGDB_MASTER_KEY = os.environ["AGDB_MASTER_KEY"]
