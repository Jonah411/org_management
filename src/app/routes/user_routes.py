from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.responses import APIResponse
from src.app.schemas.user_schema import UserCreate, UserResponse
from src.app.core.auth import get_current_user_id
from src.app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    created_user = user_service.create_new_user(
        db,
        user.model_dump()
    )

    return APIResponse(
        success=True,
        message="User created successfully",
        data=created_user,
        request_id=request.state.request_id
    )

@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_my_profile(
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = user_service.get_current_user(
        db,
        current_user_id
    )

    return APIResponse(
        success=True,
        message="User profile fetched successfully",
        data=user,
        request_id=request.state.request_id
    )