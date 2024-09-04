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
    nicknames: list[str]


class BanUnbanResponse(BaseModel):
    steamID: str
    message: str
