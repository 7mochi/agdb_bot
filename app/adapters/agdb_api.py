import httpx
from pydantic import BaseModel

from app.common import settings

agdb_api_http_client = httpx.AsyncClient(
    base_url=settings.AGDB_API_URL,
    timeout=httpx.Timeout(20),
)


class Player(BaseModel):
    steamName: str
    steamID: str
    steamUrl: str
    country: str | None = None
    relatedSteamIDs: list[str]
    avatar: str
    creationTime: int | None = None
    latestActivity: int | None = None
    isBanned: bool
    nicknames: list[str]


async def fetch_player_info(steam_id: str) -> Player | None:
    try:
        response = await agdb_api_http_client.get(f"players/{steam_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        agdb_api_response_data = response.json()

        assert agdb_api_response_data is not None
        return Player(**agdb_api_response_data)
    except Exception:
        raise
