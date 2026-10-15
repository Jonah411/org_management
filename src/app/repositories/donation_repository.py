from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.donation import Donation


def create_donation(
    db: Session,
    donation_data: dict,
) -> Donation:
    try:
        donation = Donation(**donation_data)
        db.add(donation)
        db.commit()
        db.refresh(donation)
        return donation
    except Exception:
        db.rollback()
        raise


def get_donation_by_id(
    db: Session,
    donation_id: UUID,
) -> Donation | None:
    return db.scalar(
        select(Donation).where(Donation.id == donation_id)
    )


def get_donations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Donation]:
    statement = (
        select(Donation)
        .order_by(Donation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())