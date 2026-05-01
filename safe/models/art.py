from uuid import uuid4
from pydantic import BaseModel, Field


class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    member_count: int = Field(ge=1)
    art_id: str | None = None
    velocity_history: list[int] = []


class ART(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    team_ids: list[str] = []
