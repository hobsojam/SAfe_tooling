from enum import StrEnum

from pydantic import Field

from safe.models.base import SAFeBaseModel


class TeamTopologyType(StrEnum):
    stream_aligned = "stream_aligned"
    enabling = "enabling"
    complicated_subsystem = "complicated_subsystem"
    platform = "platform"


class Team(SAFeBaseModel):
    name: str
    member_count: int = Field(ge=1)
    art_id: str | None = None
    velocity_history: list[int] = []
    topology_type: TeamTopologyType | None = None


class ART(SAFeBaseModel):
    name: str
    team_ids: list[str] = []
