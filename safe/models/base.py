from uuid import uuid4

from pydantic import BaseModel, Field


class SAFeBaseModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
