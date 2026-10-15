from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.core.auth import get_current_user_id
from src.app.core.database import get_db
from src.app.models.user_model import User


def get_current_admin(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:

    # Get authenticated user from database
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found",
        )

    # Get role name from the existing User model
    role = getattr(user, "role", None)

    if hasattr(role, "name"):
        role_name = role.name
    else:
        role_name = role

    if not role_name or str(role_name).strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user