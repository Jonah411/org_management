from sqlalchemy.orm import Session

from src.app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)

from src.app.repositories.role_repository import (
    get_role_by_id,
    get_role_by_name,
    get_all_roles,
    create_role,
    update_role,
    delete_role,
)


# ============================================================
# CREATE ROLE
# ============================================================

def create_new_role(
    db: Session,
    role_data: dict,
):

    name = role_data["name"]

    # Enum -> string
    if hasattr(name, "value"):
        name = name.value

    role_data["name"] = name

    existing_role = get_role_by_name(
        db,
        name,
    )

    if existing_role:
        raise UserAlreadyExistsException(
            "Role already exists"
        )

    return create_role(
        db,
        role_data,
    )


# ============================================================
# GET ALL ROLES
# ============================================================

def get_roles(
    db: Session,
):

    return get_all_roles(db)


# ============================================================
# GET ROLE
# ============================================================

def get_role(
    db: Session,
    role_id: int,
):

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        raise UserNotFoundException(
            "Role not found"
        )

    return role


# ============================================================
# UPDATE ROLE
# ============================================================

def update_existing_role(
    db: Session,
    role_id: int,
    role_data: dict,
):

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        raise UserNotFoundException(
            "Role not found"
        )

    # Remove fields that were not sent
    role_data = {
        key: value
        for key, value in role_data.items()
        if value is not None
    }

    if "name" in role_data:

        name = role_data["name"]

        if hasattr(name, "value"):
            name = name.value

        existing_role = get_role_by_name(
            db,
            name,
        )

        if (
            existing_role
            and existing_role.id != role_id
        ):
            raise UserAlreadyExistsException(
                "Role already exists"
            )

        role_data["name"] = name

    if not role_data:
        return role

    return update_role(
        db,
        role,
        role_data,
    )


# ============================================================
# DELETE ROLE
# ============================================================

def delete_existing_role(
    db: Session,
    role_id: int,
):

    role = get_role_by_id(
        db,
        role_id,
    )

    if not role:
        raise UserNotFoundException(
            "Role not found"
        )

    # --------------------------------------------------------
    # CHECK WHETHER ROLE IS ASSIGNED TO USERS
    # --------------------------------------------------------

    if role_has_users(
        db,
        role_id,
    ):
        raise UserAlreadyExistsException(
            "Cannot delete role because users are assigned to it"
        )

    # --------------------------------------------------------
    # DELETE ROLE
    # --------------------------------------------------------

    delete_role(
        db,
        role,
    )

    return role

