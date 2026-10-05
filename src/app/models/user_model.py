from datetime import date

from sqlalchemy import String, Integer, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    gender: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    qualification: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    occupation: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    married_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UnMarried"
    )

    marriage_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    phone_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    is_paid_chandha: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    address: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )