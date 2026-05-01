from datetime import date
from enum import Enum
from pydantic import Field
from safe.models.base import SAFeBaseModel


class PIStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    CLOSED = "closed"


class Iteration(SAFeBaseModel):
    pi_id: str
    number: int = Field(ge=1)
    name: str = ""
    start_date: date
    end_date: date
    is_ip: bool = False


class PI(SAFeBaseModel):
    name: str
    art_id: str
    start_date: date
    end_date: date
    iteration_ids: list[str] = []
    status: PIStatus = PIStatus.PLANNING
