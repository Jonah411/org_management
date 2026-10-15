from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.app.core.database import Base


class DonationType(Base):
    __tablename__ = "donation_types"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    description = Column(Text, nullable=True)

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # IMPORTANT: users.id is Integer
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )