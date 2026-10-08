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

    return (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )


# ============================================================
# GET ROLE BY NAME
# ============================================================

def get_role_by_name(
    db: Session,
    name: str,
):

    return (
        db.query(Role)
        .filter(Role.name == name)
        .first()
    )

# ============================================================
# GET ROLE BY ID
# ============================================================

def get_role_by_id(
    db: Session,
    role_id: int,
):

    return (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )


# ============================================================
# GET ALL ROLES
# ============================================================

def get_all_roles(
    db: Session,
):

    return (
        db.query(Role)
        .order_by(Role.id)
        .all()
    )


# ============================================================
# CREATE ROLE
# ============================================================

def create_role(
    db: Session,
    role_data: dict,
):

    role = Role(
        **role_data
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


# ============================================================
# UPDATE ROLE
# ============================================================

def update_role(
    db: Session,
    role: Role,
    role_data: dict,
):

    for key, value in role_data.items():
        setattr(
            role,
            key,
            value,
        )

    db.commit()
    db.refresh(role)

    return role


# ============================================================
# CHECK ROLE HAS USERS
# ============================================================

def role_has_users(
    db: Session,
    role_id: int,
) -> bool:

    user = (
        db.query(User.id)
        .filter(
            User.role_id == role_id
        )
        .first()
    )

    return user is not None


# ============================================================
# DELETE ROLE
# ============================================================

def delete_role(
    db: Session,
    role: Role,
):

    db.delete(role)
    db.commit()