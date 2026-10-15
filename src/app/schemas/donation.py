
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)


DonorName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=150,
    ),
]

PhoneNumber = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=10,
        max_length=16,
        pattern=r"^\+?[0-9]{10,15}$",
    ),
]


class PaymentMethod(str, Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class DonationCreate(BaseModel):
    donation_type_id: UUID
    donor_name: DonorName
    donor_phone: PhoneNumber | None = None
    donor_email: EmailStr | None = None
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    payment_method: PaymentMethod
    remarks: str | None = Field(
        default=None,
        max_length=1000,
    )


class DonationResponse(BaseModel):
    id: UUID
    donation_type_id: UUID
    user_id: int | None
    donor_name: str
    donor_phone: str | None
    donor_email: EmailStr | None
    amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_reference: str | None
    donation_date: datetime
    remarks: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationPaymentQRResponse(BaseModel):
    donation_id: UUID
    amount: Decimal
    payment_status: PaymentStatus
    upi_uri: str
    qr_code_data_url: str


class ManualDonationVerification(BaseModel):
    transaction_reference: str = Field(
        min_length=6,
        max_length=100,
    )
