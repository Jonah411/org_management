
from datetime import date

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Date,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.app.core.database import Base


class User(Base):

    __tablename__ = "users"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==================================================
    # USER INFORMATION
    # ==================================================

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    qualification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    occupation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    married_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UnMarried",
    )

    marriage_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # ==================================================
    # CONTACT
    # ==================================================

    phone_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ==================================================
    # PASSWORD
    # ==================================================

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ==================================================
    # ROLE FOREIGN KEY
    # ==================================================

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )

    # ==================================================
    # ROLE RELATIONSHIP
    # ==================================================

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
    )

    # ==================================================
    # OTHER
    # ==================================================

    is_paid_chandha: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

