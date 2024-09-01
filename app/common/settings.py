import os

from dotenv import load_dotenv


def read_bool(value: str) -> bool:
    return value.lower() == "true"


load_dotenv()


APP_COMPONENT = os.environ["APP_COMPONENT"]

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
AGDB_API_URL = os.environ["AGDB_API_URL"]
