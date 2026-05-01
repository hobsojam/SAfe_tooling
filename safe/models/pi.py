from datetime import date
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class PIStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    CLOSED = "closed"


class Iteration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    pi_id: str
    number: int = Field(ge=1)
    name: str = ""
    start_date: date
    end_date: date
    is_ip: bool = False


class PI(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    art_id: str
    start_date: date
    end_date: date
    iteration_ids: list[str] = []
    status: PIStatus = PIStatus.PLANNING
