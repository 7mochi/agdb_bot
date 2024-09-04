import httpx

from app.adapters.models import BanUnbanResponse, Player
from app.common import settings

agdb_api_http_client = httpx.AsyncClient(
    base_url=settings.AGDB_API_URL,
    timeout=httpx.Timeout(20),
)


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
        return None


async def ban_player(steam_id: str) -> BanUnbanResponse | None:
    try:
        response = await agdb_api_http_client.post(
            f"players/ban/{steam_id}",
            headers={"master-Key": settings.AGDB_MASTER_KEY},
        )

        response.raise_for_status()
        agdb_api_response_data = response.json()

        assert agdb_api_response_data is not None
        return BanUnbanResponse(**agdb_api_response_data)
    except Exception:
        return None


async def unban_player(steam_id: str) -> BanUnbanResponse | None:
    try:
        response = await agdb_api_http_client.post(
            f"players/unban/{steam_id}",
            headers={"master-Key": settings.AGDB_MASTER_KEY},
        )

        response.raise_for_status()
        agdb_api_response_data = response.json()

        assert agdb_api_response_data is not None
        return BanUnbanResponse(**agdb_api_response_data)
    except Exception:
        return None
