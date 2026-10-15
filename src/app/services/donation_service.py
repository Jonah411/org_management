
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.core.exceptions import (
    DonationNotFoundException,
    DonationTypeNotFoundException,
    InactiveDonationTypeException,
    InvalidDonationException,
)
from src.app.models.donation import Donation
from src.app.models.donation_type import DonationType
from src.app.models.user_model import User
from src.app.repositories.donation_repository import (
    create_donation as save_donation,
    get_donation_by_id as find_donation_by_id,
    get_donations as find_donations,
)
from src.app.schemas.donation import DonationCreate
from src.app.services.phonepe_service import create_checkout
from src.app.services.phonepe_service import get_checkout_status


def create_donation(
    db: Session,
    donation_data: DonationCreate,
    authenticated_user_id: int | None,
) -> Donation:

    donation_type = db.get(
        DonationType,
        donation_data.donation_type_id,
    )

    if donation_type is None:
        raise DonationTypeNotFoundException()

    if not donation_type.is_active:
        raise InactiveDonationTypeException()

    if authenticated_user_id is not None:
        user = db.get(User, authenticated_user_id)

        if user is None:
            raise InvalidDonationException(
                message="Authenticated user does not exist"
            )

    donation_values = donation_data.model_dump(
        exclude={"donation_type_id"}
    )

    donation_values["donation_type_id"] = donation_data.donation_type_id
    donation_values["user_id"] = authenticated_user_id
    donation_values["payment_method"] = donation_data.payment_method.value
    donation_values["payment_status"] = "PENDING"
    donation_values["transaction_reference"] = None

    try:
        return save_donation(db, donation_values)
    except Exception:
        # Keep database rollback responsibility here if repository
        # does not already perform rollback on failure.
        db.rollback()
        raise


def get_donation(
    db: Session,
    donation_id: UUID,
) -> Donation:

    donation = find_donation_by_id(db, donation_id)

    if donation is None:
        raise DonationNotFoundException()

    return donation


def list_donations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Donation]:

    return find_donations(
        db,
        skip=skip,
        limit=limit,
    )
def create_phonepe_payment(
    db: Session,
    donation_id: UUID,
    authenticated_user_id: int | None,
) -> dict:
    donation = get_donation(db, donation_id)

    if donation.payment_status != "PENDING":
        raise InvalidDonationException(
            message="Only pending donations can start a payment"
        )

    if donation.payment_method != "PHONEPE":
        raise InvalidDonationException(
            message="Donation payment method is not PhonePe"
        )

    if (
        authenticated_user_id is not None
        and donation.user_id != authenticated_user_id
    ):
        raise InvalidDonationException(
            message="You cannot pay for this donation"
        )

    # Reuse an existing merchant order rather than creating
    # multiple orders from repeated client requests.
    if donation.phonepe_merchant_order_id:
        status = get_checkout_status(
            donation.phonepe_merchant_order_id
        )
        if status.get("state") == "COMPLETED":
            raise InvalidDonationException(
                message="This donation has already been paid"
            )

        # Return status only; do not blindly create another order.
        return {
            "donation_id": str(donation.id),
            "merchant_order_id": donation.phonepe_merchant_order_id,
            "phonepe_order_id": donation.phonepe_order_id,
            "state": status.get("state"),
        }

    checkout = create_checkout(
        donation_id=str(donation.id),
        amount=donation.amount,
    )

    donation.phonepe_merchant_order_id = (
        checkout["merchant_order_id"]
    )
    donation.phonepe_order_id = checkout["phonepe_order_id"]

    try:
        db.commit()
        db.refresh(donation)
    except Exception:
        db.rollback()
        raise

    return {
        "donation_id": str(donation.id),
        "merchant_order_id": donation.phonepe_merchant_order_id,
        "phonepe_order_id": donation.phonepe_order_id,
        "state": checkout["state"],
        "redirect_url": checkout["redirect_url"],
    }