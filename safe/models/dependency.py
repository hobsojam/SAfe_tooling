from datetime import date
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class DependencyStatus(str, Enum):
    IDENTIFIED = "identified"
    RESOLVED = "resolved"
    OWNED = "owned"
    ACCEPTED = "accepted"
    MITIGATED = "mitigated"


class Dependency(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    pi_id: str
    feature_id: str | None = None
    from_team_id: str
    to_team_id: str
    iteration_id: str | None = None
    status: DependencyStatus = DependencyStatus.IDENTIFIED
    owner: str | None = None
    resolution_notes: str = ""
    raised_date: date = Field(default_factory=date.today)
    needed_by_date: date | None = None
