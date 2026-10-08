from pydantic import BaseModel, Field, SecretStr, field_validator


class LoginCreate(BaseModel):
    phone_number: str = Field(
        min_length=10,
        max_length=10
    )

    password: SecretStr = Field(
        min_length=8,
        max_length=128
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str):
        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        if not value.startswith(("6", "7", "8", "9")):
            raise ValueError(
                "Invalid Indian phone number"
            )

        return value


class LoginVerify(BaseModel):
    phone_number: str = Field(
        min_length=10,
        max_length=10
    )

    otp: str = Field(
        min_length=6,
        max_length=6
    )

    password: SecretStr = Field(
        min_length=8,
        max_length=128
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str):

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if not value.startswith(("6", "7", "8", "9")):
            raise ValueError(
                "Invalid Indian phone number"
            )

        return value

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str):

        if not value.isdigit():
            raise ValueError(
                "OTP must contain only digits"
            )

        return value


class LoginResponse(BaseModel):
    phone_number: str
    otp: str


class LoginVerifyResponse(BaseModel):
    access_token: str
    token_type: str