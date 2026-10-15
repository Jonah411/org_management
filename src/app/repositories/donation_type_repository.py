from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.app.models.donation_type import DonationType


def create_donation_type(
    db: Session,
    donation_type_data: dict,
) -> DonationType:
    donation_type = DonationType(**donation_type_data)

    db.add(donation_type)
    db.commit()
    db.refresh(donation_type)

    return donation_type


def get_donation_type_by_id(
    db: Session,
    donation_type_id: UUID,
) -> DonationType | None:
    statement = select(DonationType).where(
        DonationType.id == donation_type_id
    )

    return db.scalar(statement)


def get_donation_type_by_name(
    db: Session,
    name: str,
) -> DonationType | None:
    statement = select(DonationType).where(
        func.lower(DonationType.name) == name.strip().lower()
    )

    return db.scalar(statement)


def get_all_donation_types(
    db: Session,
    active_only: bool = False,
) -> list[DonationType]:
    statement = select(DonationType).order_by(
        DonationType.created_at.desc()
    )

    if active_only:
        statement = statement.where(
            DonationType.is_active.is_(True)
        )

    return list(db.scalars(statement).all())


def update_donation_type(
    db: Session,
    donation_type: DonationType,
    update_data: dict,
) -> DonationType:
    for field, value in update_data.items():
        setattr(donation_type, field, value)

    db.commit()
    db.refresh(donation_type)

    return donation_type


def deactivate_donation_type(
    db: Session,
    donation_type: DonationType,
) -> DonationType:
    donation_type.is_active = False

    db.commit()
    db.refresh(donation_type)

    return donation_type