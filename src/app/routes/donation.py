
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.app.core.auth import get_optional_current_user_id
from src.app.core.dependencies import get_current_admin
from src.app.core.database import get_db
from src.app.models.donation import Donation
from src.app.schemas.donation import (
    DonationCreate,
    DonationResponse,
    DonationPaymentQRResponse,
)
from src.app.services.donation_service import (
    create_donation,
    get_donation,
    list_donations,
)
from src.app.services.upi_qr_service import generate_upi_qr


router = APIRouter(
    prefix="/donations",
    tags=["Donations"],
)


@router.post(
    "",
    response_model=DonationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donation_route(
    donation_data: DonationCreate,
    db: Session = Depends(get_db),
    authenticated_user_id: int | None = Depends(
        get_optional_current_user_id
    ),
):
    return create_donation(
        db=db,
        donation_data=donation_data,
        authenticated_user_id=authenticated_user_id,
    )


@router.get(
    "",
    response_model=list[DonationResponse],
)
def list_donations_route(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return list_donations(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{donation_id}",
    response_model=DonationResponse,
)
def get_donation_route(
    donation_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return get_donation(
        db=db,
        donation_id=donation_id,
    )


@router.get(
    "/{donation_id}/upi-qr",
    response_model=DonationPaymentQRResponse,
)
def get_donation_upi_qr_route(
    donation_id: UUID,
    db: Session = Depends(get_db),
):
    donation = get_donation(
        db=db,
        donation_id=donation_id,
    )

    return generate_upi_qr(donation)


