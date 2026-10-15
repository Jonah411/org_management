from datetime import datetime
from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


DonationTypeName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=100,
    ),
]


class DonationTypeCreate(BaseModel):
    name: DonationTypeName
    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class DonationTypeUpdate(BaseModel):
    name: DonationTypeName | None = None
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    is_active: bool | None = None


class DonationTypeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
