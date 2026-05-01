from uuid import uuid4
from pydantic import BaseModel, Field, computed_field


class PIObjective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    team_id: str
    pi_id: str
    planned_business_value: int = Field(ge=1, le=10)
    actual_business_value: int | None = None
    is_stretch: bool = False
    feature_ids: list[str] = []

    @computed_field
    @property
    def is_committed(self) -> bool:
        return not self.is_stretch
