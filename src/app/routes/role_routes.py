from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.responses import APIResponse

from src.app.schemas.role_schema import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)

from src.app.services import role_service


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


# ============================================================
# CREATE ROLE
# ============================================================

@router.post(
    "",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
):

    created_role = role_service.create_new_role(
        db=db,
        role_data=role.model_dump(),
    )

    return APIResponse(
        success=True,
        message="Role created successfully",
        data=created_role,
        request_id=request.state.request_id,
    )


# ============================================================
# GET ALL ROLES
# ============================================================

@router.get(
    "",
    response_model=APIResponse[list[RoleResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_all_roles(
    request: Request,
    db: Session = Depends(get_db),
):

    roles = role_service.get_roles(db)

    return APIResponse(
        success=True,
        message="Roles fetched successfully",
        data=roles,
        request_id=request.state.request_id,
    )


# ============================================================
# GET ROLE BY ID
# ============================================================

@router.get(
    "/{role_id}",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
)
async def get_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
):

    role = role_service.get_role(
        db=db,
        role_id=role_id,
    )

    return APIResponse(
        success=True,
        message="Role fetched successfully",
        data=role,
        request_id=request.state.request_id,
    )


# ============================================================
# UPDATE ROLE
# ============================================================

@router.patch(
    "/{role_id}",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
):

    updated_role = role_service.update_existing_role(
        db=db,
        role_id=role_id,
        role_data=role.model_dump(
            exclude_unset=True
        ),
    )

    return APIResponse(
        success=True,
        message="Role updated successfully",
        data=updated_role,
        request_id=request.state.request_id,
    )


# ============================================================
# DELETE ROLE
# ============================================================

@router.delete(
    "/{role_id}",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
)
async def delete_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
):

    deleted_role = role_service.delete_existing_role(
        db=db,
        role_id=role_id,
    )

    return APIResponse(
        success=True,
        message="Role deleted successfully",
        data=deleted_role,
        request_id=request.state.request_id,
    )