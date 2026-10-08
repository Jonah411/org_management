
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from src.app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)

from src.app.repositories.user_repository import (
    get_user_by_phone,
    get_user_by_email,
    get_user_by_id,
    get_role_id_by_user_id,
    create_user,
)

from src.app.repositories.role_repository import (
    get_role_by_name,
)


# ============================================================
# PASSWORD HASHER
# ============================================================

password_hash = PasswordHash.recommended()


# ============================================================
# CREATE USER
# ============================================================

def create_new_user(
    db: Session,
    user_data: dict,
):

    # --------------------------------------------------------
    # CHECK PHONE NUMBER
    # --------------------------------------------------------

    existing_phone = get_user_by_phone(
        db,
        user_data["phone_number"],
    )

    if existing_phone:
        raise UserAlreadyExistsException(
            "Phone number already registered"
        )


    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    existing_email = get_user_by_email(
        db,
        user_data["email"],
    )

    if existing_email:
        raise UserAlreadyExistsException(
            "Email already registered"
        )


    # --------------------------------------------------------
    # GET DEFAULT MEMBER ROLE
    # --------------------------------------------------------

    member_role = get_role_by_name(
        db,
        "Member",
    )

    if not member_role:
        raise UserNotFoundException(
            "Member role not found"
        )

    user_data["role_id"] = member_role.id


    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    plain_password = user_data["password"]

    hashed_password = password_hash.hash(
        plain_password
    )

    user_data["password"] = hashed_password


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    return create_user(
        db,
        user_data,
    )


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    db: Session,
    user_id: int,
):

    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise UserNotFoundException(
            "User not found"
        )

    return user


# ============================================================
# GET ROLE ID BY USER ID
# ============================================================

def get_current_user_role_id(
    db: Session,
    user_id: int,
):

    # --------------------------------------------------------
    # GET ROLE ID
    # --------------------------------------------------------

    role_id = get_role_id_by_user_id(
        db,
        user_id,
    )

    # --------------------------------------------------------
    # ROLE NOT ASSIGNED
    # --------------------------------------------------------

    if role_id is None:
        raise UserNotFoundException(
            "Role not assigned to user"
        )

    return role_id

