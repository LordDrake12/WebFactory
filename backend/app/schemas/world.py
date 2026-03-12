from pydantic import BaseModel, Field


class CreateWorldRequest(BaseModel):
    code: str = Field(min_length=3, max_length=32)
    name: str = Field(min_length=1, max_length=64)
    is_public: bool = False


class JoinWorldRequest(BaseModel):
    code: str


class UpdateWorldSettingsRequest(BaseModel):
    settings: dict


class ExpandWorldRequest(BaseModel):
    add_w: int = Field(ge=1, le=256)
    add_h: int = Field(ge=1, le=256)


class WorldSummary(BaseModel):
    id: int
    code: str
    name: str
    owner_id: int
    is_public: bool
    max_players: int
    size_w: int
    size_h: int
    expansion_level: int


class WorldSnapshot(BaseModel):
    world: WorldSummary
    settings: dict
    state: dict
