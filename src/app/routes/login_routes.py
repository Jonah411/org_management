from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.orm import Session

from src.app.core.responses import APIResponse

from src.app.schemas.login_schema import (
    LoginCreate,
    LoginResponse,
    LoginVerify,
    LoginVerifyResponse
)

from src.app.core.database import get_db

from src.app.services import login_service


router = APIRouter(
    prefix="/login",
    tags=["Login"]
)


@router.post(
    "",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK
)
async def create_login(
    login_data: LoginCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    login_result = await login_service.create_login(
        db,
        login_data.model_dump()
    )

    return APIResponse(
        success=True,
        message="OTP sent successfully",
        data=login_result,
        request_id=request.state.request_id,
    )


@router.post(
    "/verify",
    response_model=APIResponse[LoginVerifyResponse],
    status_code=status.HTTP_200_OK
)
async def verify_login(
    login_data: LoginVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    login_result = login_service.verify_login(
        db,
        login_data.model_dump()
    )

    return APIResponse(
        success=True,
        message="Login successful",
        data=login_result,
        request_id=request.state.request_id,
    )