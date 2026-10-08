
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# ============================================================
# COMMON PASSWORD VALIDATION
# ============================================================

def validate_password(value: str) -> str:
    value = value.strip()

    if len(value) < 8:
        raise ValueError(
            "Password must contain at least 8 characters"
        )

    if not any(char.isupper() for char in value):
        raise ValueError(
            "Password must contain at least one uppercase letter"
        )

    if not any(char.islower() for char in value):
        raise ValueError(
            "Password must contain at least one lowercase letter"
        )

    if not any(char.isdigit() for char in value):
        raise ValueError(
            "Password must contain at least one number"
        )

    return value


# ============================================================
# USER CREATE
# ============================================================

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

    dob: date

    married_status: str = Field(
        default="UnMarried",
        min_length=1,
        max_length=20
    )

    marriage_date: date | None = None

    phone_number: str = Field(
        min_length=10,
        max_length=10
    )

    email: EmailStr

    address: str | None = Field(
        default=None,
        min_length=10,
        max_length=100
    )

    password: str = Field(
        min_length=8,
        max_length=100
    )

    is_paid_chandha: bool = False
    role_id: int | None = Field( 
        default=None, 
        gt=0, 
    )
    # --------------------------------------------------------
    # FIRST NAME
    # --------------------------------------------------------

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "First name cannot be empty"
            )

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "First name must contain only letters"
            )

        return value


    # --------------------------------------------------------
    # LAST NAME
    # --------------------------------------------------------

    @field_validator("last_name")
    @classmethod
    def validate_last_name(
        cls,
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Last name must contain only letters"
            )

        return value


    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: EmailStr
    ) -> str:

        return str(value).lower()


    # --------------------------------------------------------
    # PHONE NUMBER
    # --------------------------------------------------------

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(
        cls,
        value: str
    ) -> str:

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        if not value.startswith(
            ("6", "7", "8", "9")
        ):
            raise ValueError(
                "Invalid Indian phone number"
            )

        return value


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    @field_validator("password")
    @classmethod
    def validate_password_field(
        cls,
        value: str
    ) -> str:

        return validate_password(value)


    # --------------------------------------------------------
    # MARRIED STATUS
    # --------------------------------------------------------

    @field_validator("married_status")
    @classmethod
    def validate_married_status(
        cls,
        value: str
    ) -> str:

        value = value.strip()

        allowed_status = {
            "Married",
            "UnMarried"
        }

        if value not in allowed_status:
            raise ValueError(
                "married_status must be Married or UnMarried"
            )

        return value


    # --------------------------------------------------------
    # DOB + AGE VALIDATION
    # --------------------------------------------------------

    @model_validator(mode="after")
    def validate_age_and_dob(self):

        today = date.today()

        calculated_age = (
            today.year
            - self.dob.year
            - (
                (today.month, today.day)
                < (self.dob.month, self.dob.day)
            )
        )

        if calculated_age != self.age:
            raise ValueError(
                "Age does not match the date of birth"
            )

        if self.dob > today:
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        return self


    # --------------------------------------------------------
    # MARRIAGE VALIDATION
    # --------------------------------------------------------

    @model_validator(mode="after")
    def validate_marriage_details(self):

        if (
            self.married_status == "Married"
            and not self.marriage_date
        ):
            raise ValueError(
                "Marriage date is required when "
                "married_status is Married"
            )

        if (
            self.married_status == "UnMarried"
            and self.marriage_date
        ):
            raise ValueError(
                "Marriage date must not be provided "
                "when married_status is UnMarried"
            )

        if (
            self.marriage_date
            and self.marriage_date > date.today()
        ):
            raise ValueError(
                "Marriage date cannot be in the future"
            )

        return self


# ============================================================
# USER UPDATE
# ============================================================

class UserUpdate(BaseModel):

    first_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    last_name: str | None = Field(
        default=None,
        max_length=50
    )

    email: EmailStr | None = None

    age: int | None = Field(
        default=None,
        ge=8,
        le=100
    )

    gender: str | None = Field(
        default=None,
        min_length=1,
        max_length=10
    )

    qualification: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    occupation: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )

    dob: date | None = None

    married_status: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )

    marriage_date: date | None = None

    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    address: str | None = Field(
        default=None,
        min_length=10,
        max_length=100
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=100
    )

    is_paid_chandha: bool | None = None


    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str | None):

        if value is None:
            return None

        value = value.strip()

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "First name must contain only letters"
            )

        return value


    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str | None):

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Last name must contain only letters"
            )

        return value


    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: EmailStr | None
    ):

        if value is None:
            return None

        return str(value).lower()


    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(
        cls,
        value: str | None
    ):

        if value is None:
            return None

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        if not value.startswith(
            ("6", "7", "8", "9")
        ):
            raise ValueError(
                "Invalid Indian phone number"
            )

        return value


    @field_validator("password")
    @classmethod
    def validate_password_field(
        cls,
        value: str | None
    ):

        if value is None:
            return None

        return validate_password(value)


    @field_validator("married_status")
    @classmethod
    def validate_married_status(
        cls,
        value: str | None
    ):

        if value is None:
            return None

        value = value.strip()

        if value not in {
            "Married",
            "UnMarried"
        }:
            raise ValueError(
                "married_status must be Married or UnMarried"
            )

        return value


# ============================================================
# USER RESPONSE
# ============================================================

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


# ============================================================
# REGISTER USER
# ============================================================

class RegisterUser(BaseModel):

    userName: str = Field(
        min_length=3,
        max_length=20
    )

    password: str = Field(
        min_length=8,
        max_length=100
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=100
    )


    @field_validator("password")
    @classmethod
    def validate_password_field(
        cls,
        value: str
    ) -> str:

        return validate_password(value)


    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(
        cls,
        value: str
    ) -> str:

        return value.strip()


    @model_validator(mode="after")
    def validate_user_data(self):

        if self.password != self.confirm_password:
            raise ValueError(
                "Password and confirm password do not match"
            )

        return self

