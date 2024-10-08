from pydantic import BaseModel


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
    banReason: str | None = None
    nicknames: list[str]


class Server(BaseModel):
    id: int
    ipPort: str
    serverName: str
    agdbVersion: str


class BanUnbanResponse(BaseModel):
    steamID: str
    message: str
