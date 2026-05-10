from datetime import date
from enum import StrEnum

from pydantic import Field

from safe.models.base import SAFeBaseModel


class DependencyStatus(StrEnum):
    IDENTIFIED = "identified"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Dependency(SAFeBaseModel):
    description: str
    pi_id: str
    from_feature_id: str
    to_feature_id: str
    status: DependencyStatus = DependencyStatus.IDENTIFIED
    owner: str | None = None
    resolution_notes: str = ""
    raised_date: date = Field(default_factory=date.today)
    needed_by_date: date | None = None
