from datetime import date
from enum import Enum
from pydantic import Field
from safe.models.base import SAFeBaseModel


class ROAMStatus(str, Enum):
    RESOLVED = "resolved"
    OWNED = "owned"
    ACCEPTED = "accepted"
    MITIGATED = "mitigated"
    UNROAMED = "unroamed"


class Risk(SAFeBaseModel):
    description: str
    pi_id: str
    team_id: str | None = None
    feature_id: str | None = None
    roam_status: ROAMStatus = ROAMStatus.UNROAMED
    owner: str | None = None
    mitigation_notes: str = ""
    raised_date: date = Field(default_factory=date.today)
