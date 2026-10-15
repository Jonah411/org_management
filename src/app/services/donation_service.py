
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.core.exceptions import (
    DonationNotFoundException,
    DonationTypeNotFoundException,
    InactiveDonationTypeException,
    InvalidDonationException,
    PhonePePaymentException,
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
from src.app.services.phonepe_service import (
    create_checkout,
    get_checkout_status,
)


def _normalize(value) -> str:
    return str(getattr(value, "value", value)).strip().upper()


def _verify_amount(
    donation_amount,
    gateway_amount,
) -> bool:
    """
    Database amount: INR.
    PhonePe amount: paise.
    """
    try:
        expected_paise = int(
            Decimal(str(donation_amount)) * 100
        )
        received_paise = int(gateway_amount)

        return expected_paise == received_paise

    except (ValueError, TypeError, ArithmeticError):
        return False


def create_donation(
    db: Session,
    donation_data: DonationCreate,
    authenticated_user_id: int | None,
):
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
        exclude={
            "donation_type_id",
            "payment_method",
        }
    )

    donation_values["donation_type_id"] = (
        donation_data.donation_type_id
    )
    donation_values["user_id"] = authenticated_user_id
    donation_values["payment_method"] = _normalize(
        donation_data.payment_method
    )
    donation_values["payment_status"] = "PENDING"
    donation_values["transaction_reference"] = None

    try:
        return save_donation(db, donation_values)

    except Exception:
        db.rollback()
        raise


def get_donation(
    db: Session,
    donation_id: UUID,
):
    donation = find_donation_by_id(
        db,
        donation_id,
    )

    if donation is None:
        raise DonationNotFoundException()

    return donation


def list_donations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
):
    return find_donations(
        db,
        skip=skip,
        limit=limit,
    )


async def create_phonepe_payment(
    db: Session,
    donation_id: UUID,
    authenticated_user_id: int | None,
):
    donation = get_donation(
        db,
        donation_id,
    )

    # Check ownership before contacting the payment gateway.
    if (
        authenticated_user_id is not None
        and donation.user_id != authenticated_user_id
    ):
        raise InvalidDonationException(
            message="You cannot pay for this donation"
        )

    if _normalize(donation.payment_method) != "PHONEPE":
        raise InvalidDonationException(
            message="Donation payment method is not PhonePe"
        )

    if _normalize(donation.payment_status) == "SUCCESS":
        raise InvalidDonationException(
            message="This donation has already been paid"
        )

    if _normalize(donation.payment_status) != "PENDING":
        raise InvalidDonationException(
            message="Only pending donations can start a payment"
        )

    # Reuse the existing PhonePe order if one has already been created.
    if donation.phonepe_merchant_order_id:
        try:
            status_data = get_checkout_status(
                donation.phonepe_merchant_order_id
            )

        except Exception as exc:
            raise PhonePePaymentException(
                "Unable to retrieve PhonePe payment status"
            ) from exc

        gateway_order_id = (
            status_data.get("merchantOrderId")
            or status_data.get("merchant_order_id")
        )

        if (
            gateway_order_id
            and gateway_order_id
            != donation.phonepe_merchant_order_id
        ):
            raise PhonePePaymentException(
                "PhonePe returned a different merchant order ID"
            )

        gateway_state = _normalize(
            status_data.get("state", "")
        )

        if gateway_state in {"COMPLETED", "SUCCESS"}:
            if not _verify_amount(
                donation.amount,
                status_data.get("amount"),
            ):
                raise PhonePePaymentException(
                    "PhonePe payment amount does not match the donation"
                )

            # Do not mark SUCCESS here based only on the checkout
            # response. Use the verified webhook/status flow to update it.
            return {
                "donation_id": str(donation.id),
                "merchant_order_id": (
                    donation.phonepe_merchant_order_id
                ),
                "phonepe_order_id": donation.phonepe_order_id,
                "state": gateway_state,
                "message": (
                    "Payment appears completed. "
                    "Verify the payment details before updating the donation."
                ),
            }

        if gateway_state in {"FAILED", "EXPIRED"}:
            raise InvalidDonationException(
                message=(
                    "The existing PhonePe order has failed or expired. "
                    "Check the payment status before creating another order."
                )
            )

        return {
            "donation_id": str(donation.id),
            "merchant_order_id": (
                donation.phonepe_merchant_order_id
            ),
            "phonepe_order_id": donation.phonepe_order_id,
            "state": gateway_state or "PENDING",
            "message": "Existing PhonePe checkout order found",
        }

    try:
        checkout = create_checkout(
            donation_id=str(donation.id),
            amount=donation.amount,
        )

        merchant_order_id = checkout.get("merchant_order_id")
        if not merchant_order_id:
            raise PhonePePaymentException(
                "PhonePe did not return a merchant order ID"
            )

        donation.phonepe_merchant_order_id = merchant_order_id
        donation.phonepe_order_id = checkout.get(
            "phonepe_order_id"
        )

        db.commit()
        db.refresh(donation)

        return {
            "donation_id": str(donation.id),
            "merchant_order_id": (
                donation.phonepe_merchant_order_id
            ),
            "phonepe_order_id": donation.phonepe_order_id,
            "state": checkout.get("state") or "PENDING",
            "redirect_url": checkout["redirect_url"],
        }

    except PhonePePaymentException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise PhonePePaymentException(
            "Unable to create PhonePe checkout"
        ) from exc
