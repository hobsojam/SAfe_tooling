from enum import StrEnum

from pydantic import Field, computed_field

from safe.models.base import SAFeBaseModel


class FeatureStatus(StrEnum):
    FUNNEL = "funnel"
    ANALYZING = "analyzing"
    BACKLOG = "backlog"
    IMPLEMENTING = "implementing"
    DONE = "done"


class Feature(SAFeBaseModel):
    name: str
    description: str = ""
    pi_id: str | None = None
    team_id: str | None = None
    iteration_id: str | None = None
    status: FeatureStatus = FeatureStatus.BACKLOG
    acceptance_criteria: str = ""
    story_ids: list[str] = []
    dependency_ids: list[str] = []
    user_business_value: int = Field(ge=1, le=10)
    time_criticality: int = Field(ge=1, le=10)
    risk_reduction_opportunity_enablement: int = Field(ge=1, le=10)
    job_size: int = Field(ge=1, le=13)

    @computed_field
    @property
    def cost_of_delay(self) -> int:
        return (
            self.user_business_value
            + self.time_criticality
            + self.risk_reduction_opportunity_enablement
        )

    # Pydantic V2 style for making fields optional.
    # Note: For related objects, a dedicated API/Service method should handle the actual write.

    @computed_field
    @property
    def wsjf_score(self) -> float:
        return round(self.cost_of_delay / self.job_size, 2)

# ... (rest of the file)


class StoryStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ACCEPTED = "accepted"


class Story(SAFeBaseModel):
    name: str
    description: str = ""
    feature_id: str
    team_id: str
    iteration_id: str | None = None
    points: int = Field(ge=1)
    status: StoryStatus = StoryStatus.NOT_STARTED
    acceptance_criteria: str = ""
