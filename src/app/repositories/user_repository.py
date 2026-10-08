
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.user_model import User


# ============================================================
# GET USER BY PHONE
# ============================================================

def get_user_by_phone(
    db: Session,
    phone_number: str,
):
    stmt = select(User).where(
        User.phone_number == phone_number
    )

    return db.scalar(stmt)


# ============================================================
# GET USER BY EMAIL
# ============================================================

def get_user_by_email(
    db: Session,
    email: str,
):
    stmt = select(User).where(
        User.email == email
    )

    return db.scalar(stmt)


# ============================================================
# GET USER BY ID
# ============================================================

def get_user_by_id(
    db: Session,
    user_id: int,
):
    stmt = select(User).where(
        User.id == user_id
    )

    return db.scalar(stmt)


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    db: Session,
    user_data: dict,
):
    db_user = User(**user_data)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except Exception:
        db.rollback()
        raise

# ============================================================
# GET ROLE ID BY USER ID
# ============================================================

def get_role_id_by_user_id(
    db: Session,
    user_id: int,
):
    stmt = select(User.role_id).where(
        User.id == user_id
    )

    return db.scalar(stmt)



