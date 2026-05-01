from pydantic import Field
from safe.models.base import SAFeBaseModel


class Team(SAFeBaseModel):
    name: str
    member_count: int = Field(ge=1)
    art_id: str | None = None
    velocity_history: list[int] = []


class ART(SAFeBaseModel):
    name: str
    team_ids: list[str] = []
