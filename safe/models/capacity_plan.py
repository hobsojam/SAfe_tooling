from pydantic import Field, computed_field
from safe.logic.capacity import available_capacity as _available_capacity
from safe.models.base import SAFeBaseModel


class CapacityPlan(SAFeBaseModel):
    team_id: str
    iteration_id: str
    pi_id: str
    team_size: int = Field(ge=1)
    iteration_days: int = Field(ge=1, default=10)
    pto_days: float = Field(ge=0.0, default=0.0)
    overhead_pct: float = Field(ge=0.0, le=1.0, default=0.2)

    @computed_field
    @property
    def available_capacity(self) -> float:
        return _available_capacity(self.team_size, self.iteration_days, self.pto_days, self.overhead_pct)
