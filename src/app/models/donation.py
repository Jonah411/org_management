import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Numeric,
    Uuid,
    Integer
)
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    donation_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("donation_types.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    donor_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    donor_phone: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )

    donor_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False,
    )

    transaction_reference: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        unique=True,
    )

    donation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    phonepe_merchant_order_id: Mapped[str | None] = mapped_column(
        String(63),
        unique=True,
        index=True,
        nullable=True,
    )

    phonepe_order_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Manual verification audit
    verified_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )