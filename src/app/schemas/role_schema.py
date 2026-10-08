from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class RoleName(str, Enum):

    ADMIN = "Admin"
    STAFF = "Staff"
    MEMBER = "Member"


class RoleCreate(BaseModel):

    name: RoleName

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value):

        if not isinstance(value, str):
            raise ValueError(
                "Role name must be a string"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                "Role name cannot be empty"
            )

        return value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ):

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


class RoleUpdate(BaseModel):

    name: RoleName | None = None

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value):

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "Role name must be a string"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                "Role name cannot be empty"
            )

        return value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ):

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


class RoleResponse(BaseModel):

    id: int
    name: RoleName
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )