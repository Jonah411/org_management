from pydantic import BaseModel,Field,EmailStr,field_validator,model_validator,ConfigDict
from datetime import date

class UserCreate(BaseModel):

    first_name: str = Field(
        min_length=3,
        max_length=50
    )

    last_name: str | None = Field(
        default=None,
        max_length=50
    )

    age: int = Field(
        ge=8,
        le=100
    )

    gender: str = Field(
        min_length=1,
        max_length=10
    )

    qualification: str = Field(
        min_length=1,
        max_length=50
    )

    occupation: str = Field(
        min_length=1,
        max_length=20
    )

    dob: str = Field(
        min_length=1,
        max_length=20
    )

    married_status: str = Field(
        default="UnMarried",
        min_length=1,
        max_length=20
    )

    marriage_date: str | None = Field(
        default=None,
        max_length=20
    )

    phone_number: str = Field(
        min_length=10,
        max_length=15
    )

    email: EmailStr

    address: str | None = Field(
        default=None,
        min_length=10,
        max_length=100
    )

    is_paid_chandha: bool = False

    @field_validator("first_name")
    @classmethod
    def validate_names(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Name must contain only letters"
            )

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: EmailStr):

        return str(value).lower()

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

    @field_validator("married_status")
    @classmethod
    def validate_married_status(cls, value: str):

        allowed_status = {
            "Married",
            "UnMarried"
        }

        if value not in allowed_status:
            raise ValueError(
                "married_status must be Married or UnMarried"
            )

        return value

    @model_validator(mode="after")
    def validate_marriage_details(self):

        if (
            self.married_status == "Married"
            and not self.marriage_date
        ):
            raise ValueError(
                "Marriage date is required when married_status is Married"
            )

        if (
            self.married_status == "UnMarried"
            and self.marriage_date
        ):
            raise ValueError(
                "Marriage date must not be provided when married_status is UnMarried"
            )

        return self

class UserUpdate(BaseModel):
    name: str | None = Field(
        default= None,
        min_length=3,
        max_length=50
    )
    email: EmailStr | None = None
    address: str | None = Field(
        default= None,
        min_length=3,
        max_length=50
    )
    age: int | None = Field(
        default=None,
        ge=18,
        le=100
    )


class UserResponse(BaseModel):

    id: int

    first_name: str
    last_name: str | None

    age: int
    gender: str
    qualification: str
    occupation: str

    dob: date

    married_status: str
    marriage_date: date | None

    phone_number: str
    email: EmailStr

    address: str | None

    is_paid_chandha: bool

    image: str | None

    model_config = ConfigDict(
        from_attributes=True
    )

class  RegisterUser(BaseModel):
    userName:str = Field(
        min_length=3,
        max_length=20
    )
    password: str = Field(
        min_length=5
    )
    confirm_password: str = Field(
        min_length=5
    )
    @model_validator(mode="after")
    def validate_user_data(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match")
        return self