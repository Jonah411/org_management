from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.user_model import User


def get_user_by_phone(
    db: Session,
    phone_number: str
):
    stmt = select(User).where(
        User.phone_number == phone_number
    )

    return db.scalar(stmt)


def get_user_by_email(
    db: Session,
    email: str
):
    stmt = select(User).where(
        User.email == email
    )

    return db.scalar(stmt)


def create_user(
    db: Session,
    user_data: dict
):
    db_user = User(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_id(
    db: Session,
    user_id: int
):
    stmt = select(User).where(
        User.id == user_id
    )

    return db.scalar(stmt)