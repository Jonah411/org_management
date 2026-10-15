from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.schemas.donation_type import (
    DonationTypeCreate,
    DonationTypeUpdate,
    DonationTypeResponse,
)
from src.app.services import donation_type_service as service

# Replace this import with your existing admin authentication dependency.
from src.app.core.dependencies import get_current_admin


router = APIRouter(
    prefix="/donation-types",
    tags=["Donation Types"],
)


@router.post(
    "",
    response_model=DonationTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donation_type(
    data: DonationTypeCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.create_donation_type(
        db=db,
        data=data,
        admin_user_id=admin.id,
    )


@router.get(
    "",
    response_model=list[DonationTypeResponse],
)
def get_all_donation_types(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_all_donation_types(
        db=db,
        active_only=active_only,
    )


@router.get(
    "/{donation_type_id}",
    response_model=DonationTypeResponse,
)
def get_donation_type(
    donation_type_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_donation_type(
        db=db,
        donation_type_id=donation_type_id,
    )


@router.patch(
    "/{donation_type_id}",
    response_model=DonationTypeResponse,
)
def update_donation_type(
    donation_type_id: UUID,
    data: DonationTypeUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.update_donation_type(
        db=db,
        donation_type_id=donation_type_id,
        data=data,
    )


@router.patch(
    "/{donation_type_id}/deactivate",
    response_model=DonationTypeResponse,
)
def deactivate_donation_type(
    donation_type_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.deactivate_donation_type(
        db=db,
        donation_type_id=donation_type_id,
    )