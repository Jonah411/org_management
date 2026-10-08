
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.role_model import Role
from src.app.models.user_model import User


# ============================================================
# GET ROLE BY ID
# ============================================================

def get_role_by_id(
    db: Session,
    role_id: int,
):
    stmt = select(Role).where(
        Role.id == role_id
    )

    return db.scalar(stmt)


# ============================================================
# GET ROLE BY NAME
# ============================================================

def get_role_by_name(
    db: Session,
    name: str,
):
    stmt = select(Role).where(
        Role.name == name
    )

    return db.scalar(stmt)


# ============================================================
# GET ALL ROLES
# ============================================================

def get_all_roles(
    db: Session,
):
    stmt = select(Role).order_by(
        Role.id
    )

    return list(
        db.scalars(stmt).all()
    )


# ============================================================
# CREATE ROLE
# ============================================================

def create_role(
    db: Session,
    role_data: dict,
):
    db_role = Role(**role_data)

    try:
        db.add(db_role)
        db.commit()
        db.refresh(db_role)

        return db_role

    except Exception:
        db.rollback()
        raise


# ============================================================
# UPDATE ROLE
# ============================================================

def update_role(
    db: Session,
    role,
    role_data: dict,
):
    try:

        for key, value in role_data.items():
            setattr(
                role,
                key,
                value,
            )

        db.commit()
        db.refresh(role)

        return role

    except Exception:
        db.rollback()
        raise


# ============================================================
# CHECK ROLE ASSIGNED TO USERS
# ============================================================

def role_has_users(
    db: Session,
    role_id: int,
) -> bool:

    stmt = select(
        User.id
    ).where(
        User.role_id == role_id
    ).limit(1)

    return db.scalar(stmt) is not None


# ============================================================
# DELETE ROLE
# ============================================================

def delete_role(
    db: Session,
    role,
):
    try:

        db.delete(role)
        db.commit()

    except Exception:
        db.rollback()
        raise

