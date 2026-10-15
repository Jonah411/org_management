import logging
from datetime import datetime, timezone
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.core.auth import get_current_user_id
from src.app.core.database import get_db
from src.app.core.exceptions import (
    AppException,
    AuthorizationException,
    DonationNotFoundException,
    InvalidDonationException,
    PaymentEventConflictException,
    PaymentGatewayUnavailableException,
)
from src.app.models.donation import Donation
from src.app.models.user_model import User
from src.app.services.donation_service import create_phonepe_payment


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/donations",
    tags=["Donation Payments"],
)


class ManualDonationVerification(BaseModel):
    transaction_reference: str = Field(
        min_length=6,
        max_length=100,
    )


def _normalized(value) -> str:
    return str(getattr(value, "value", value)).upper()


def require_admin(
    db: Session,
    user_id: int,
) -> User:
    user = db.get(User, user_id)

    if user is None:
        raise AuthorizationException(
            "Authenticated user was not found"
        )

    role = getattr(user, "role", None)
    role_name = getattr(role, "name", role)

    if str(role_name).strip().lower() != "admin":
        raise AuthorizationException(
            "Admin access is required"
        )

    return user


@router.post("/{donation_id}/verify-manual")
def verify_manual_donation(
    donation_id: UUID,
    body: ManualDonationVerification,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_user_id),
):
    require_admin(db, admin_id)

    transaction_reference = body.transaction_reference.strip()

    if not transaction_reference:
        raise InvalidDonationException(
            message="Transaction reference is required"
        )

    try:
        donation = (
            db.query(Donation)
            .filter(Donation.id == donation_id)
            .with_for_update()
            .first()
        )

        if donation is None:
            raise DonationNotFoundException()

        if _normalized(donation.payment_method) != "UPI":
            raise InvalidDonationException(
                message="Manual verification is only for UPI donations"
            )

        if _normalized(donation.payment_status) == "SUCCESS":
            raise PaymentEventConflictException(
                "Donation is already marked successful"
            )

        if _normalized(donation.payment_status) != "PENDING":
            raise PaymentEventConflictException(
                "Only pending donations can be verified"
            )

        existing_donation = (
            db.query(Donation)
            .filter(
                Donation.transaction_reference == transaction_reference,
                Donation.id != donation_id,
            )
            .first()
        )

        if existing_donation is not None:
            raise PaymentEventConflictException(
                "This transaction reference is already used"
            )

        # Verify the transaction against trusted bank/UPI records first.
        donation.transaction_reference = transaction_reference
        donation.payment_status = "SUCCESS"
        donation.verified_by_user_id = admin_id
        donation.verified_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(donation)

        return {
            "success": True,
            "message": "Manual UPI donation verified",
            "data": {
                "donation_id": str(donation.id),
                "payment_status": _normalized(
                    donation.payment_status
                ),
                "transaction_reference": donation.transaction_reference,
                "verified_by_user_id": admin_id,
                "verified_at": donation.verified_at,
            },
        }

    except AppException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        logger.exception(
            "Manual donation verification failed for %s",
            donation_id,
        )
        raise


@router.post("/{donation_id}/phonepe")
async def start_phonepe_payment(
    donation_id: UUID,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        data = await create_phonepe_payment(
            db=db,
            donation_id=donation_id,
            authenticated_user_id=user_id,
        )

        return {
            "success": True,
            "message": "PhonePe checkout initialized",
            "data": data,
        }

    except AppException:
        raise

    except httpx.HTTPError as exc:
        logger.exception(
            "PhonePe checkout request failed for donation %s",
            donation_id,
        )
        raise PaymentGatewayUnavailableException() from exc

    except (ValueError, TypeError) as exc:
        logger.exception(
            "Invalid PhonePe checkout data for donation %s",
            donation_id,
        )
        raise InvalidDonationException(
            message="Unable to initialize this donation payment"
        ) from exc

    except Exception as exc:
        logger.exception(
            "PhonePe checkout initialization failed for donation %s",
            donation_id,
        )
        raise PaymentGatewayUnavailableException() from exc
