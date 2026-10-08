
from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.app.core.database import Base


class Role(Base):

    __tablename__ = "roles"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==================================================
    # ROLE INFORMATION
    # ==================================================

    name: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ==================================================
    # USERS RELATIONSHIP
    # ==================================================

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
    )

