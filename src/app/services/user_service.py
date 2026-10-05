from sqlalchemy.orm import Session

from src.app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException
)
from src.app.repositories.user_repository import (
    get_user_by_phone,
    get_user_by_email,
    get_user_by_id,
    create_user
)



def create_new_user(
    db: Session,
    user_data: dict
):

    # Check phone number
    existing_phone = get_user_by_phone(
        db,
        user_data["phone_number"]
    )

    if existing_phone:
        raise UserAlreadyExistsException(
                "Phone number already registered"
        )

    # Check email
    existing_email = get_user_by_email(
        db,
        user_data["email"]
    )

    if existing_email:    
        raise UserAlreadyExistsException(
            "Email already registered"
        )

    # Create user
    return create_user(
        db,
        user_data
    )
def get_current_user(
    db: Session,
    user_id: int
):
    user = get_user_by_id(
        db,
        user_id
    )

    if not user:
        raise UserNotFoundException(
            "User not found"
        )

    return user