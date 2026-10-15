import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.security import settings
from src.app.core.exceptions import (
    AppException,
    DonationNotFoundException,
    InvalidPaymentWebhookException,
    PaymentGatewayUnavailableException,
    PhonePePaymentException,
)
from src.app.models.donation import Donation
from src.app.models.payment_webhook_event import PaymentWebhookEvent
from src.app.services.phonepe_service import get_checkout_status


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["Payment Webhooks"],
)

SUPPORTED_EVENTS = {
    "checkout.order.completed",
    "checkout.order.failed",
}


def normalize_status(value) -> str:
    """Normalize Enum or string values."""
    return str(getattr(value, "value", value) or "").strip().upper()


def verify_phonepe_webhook_auth(
    authorization: str | None,
) -> bool:
    """
    Validate SHA-256(username:password).

    IMPORTANT:
    This must match the authentication format configured for
    your actual PhonePe PG webhook. Do not assume all PhonePe
    integrations use this exact format.
    """
    username = settings.PHONEPE_WEBHOOK_USERNAME
    password = settings.PHONEPE_WEBHOOK_PASSWORD

    if not username or not password or not authorization:
        return False

    expected = hashlib.sha256(
        f"{username}:{password}".encode("utf-8")
    ).hexdigest()

    provided = authorization.strip()

    if provided.lower().startswith("sha256 "):
        provided = provided[7:].strip()

    return hmac.compare_digest(expected, provided)


def verify_amount(donation: Donation, gateway_amount) -> None:
    """
    Assumption:
    donation.amount is stored in rupees.
    PhonePe checkout amount is returned in paise.
    """
    if gateway_amount is None:
        raise PhonePePaymentException(
            "Payment amount is missing from PhonePe response"
        )

    try:
        expected_paise = int(round(float(donation.amount) * 100))
        actual_paise = int(gateway_amount)
    except (TypeError, ValueError, OverflowError) as exc:
        raise PhonePePaymentException(
            "Invalid payment amount received from PhonePe"
        ) from exc

    if expected_paise != actual_paise:
        logger.warning(
            "PhonePe amount mismatch for donation_id=%s",
            donation.id,
        )
        raise PhonePePaymentException(
            "Payment amount does not match the donation amount"
        )


def get_completed_transaction_reference(
    verified: dict,
) -> str | None:
    """
    Extract a transaction reference from the verified order response.
    Check the actual PhonePe response schema for your PG integration.
    """
    payment_details = verified.get("paymentDetails") or []

    if not isinstance(payment_details, list):
        raise InvalidPaymentWebhookException(
            "Invalid payment details from PhonePe"
        )

    expected_amount = verified.get("amount")

    for payment in payment_details:
        if not isinstance(payment, dict):
            continue

        if normalize_status(payment.get("state")) != "COMPLETED":
            continue

        payment_amount = payment.get("amount")

        if payment_amount is None or expected_amount is None:
            continue

        try:
            if int(payment_amount) != int(expected_amount):
                continue
        except (TypeError, ValueError, OverflowError):
            continue

        transaction_reference = (
            payment.get("transactionId")
            or payment.get("rail", {}).get("utr")
            if isinstance(payment.get("rail"), dict)
            else payment.get("transactionId")
        )

        if transaction_reference:
            return str(transaction_reference)

    return None


@router.post("/phonepe")
async def phonepe_webhook(
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # 1. Authenticate webhook request.
    if not verify_phonepe_webhook_auth(authorization):
        logger.warning(
            "PhonePe webhook authentication failed; header_present=%s",
            bool(authorization),
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid PhonePe webhook authentication",
        )

    # 2. Read raw request body for validation and idempotency.
    raw_body = await request.body()

    try:
        body = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise InvalidPaymentWebhookException(
            "Invalid webhook JSON"
        )

    if not isinstance(body, dict):
        raise InvalidPaymentWebhookException(
            "Webhook body must be a JSON object"
        )

    event_type = body.get("event")
    payload = body.get("payload")

    if not isinstance(payload, dict):
        raise InvalidPaymentWebhookException(
            "Webhook payload is missing"
        )

    merchant_order_id = payload.get("merchantOrderId")

    if not event_type or not merchant_order_id:
        raise InvalidPaymentWebhookException(
            "Webhook event or merchant order ID is missing"
        )

    # 3. Ignore events that do not concern order completion/failure.
    if event_type not in SUPPORTED_EVENTS:
        return {
            "success": True,
            "message": "Webhook event ignored",
        }

    event_hash = hashlib.sha256(raw_body).hexdigest()

    try:
        # 4. Ignore exact webhook deliveries already processed.
        duplicate = (
            db.query(PaymentWebhookEvent)
            .filter(PaymentWebhookEvent.event_hash == event_hash)
            .first()
        )

        if duplicate:
            return {
                "success": True,
                "message": "Duplicate webhook ignored",
            }

        # 5. Locate and lock the donation using our merchant order ID.
        donation = (
            db.query(Donation)
            .filter(
                Donation.phonepe_merchant_order_id
                == merchant_order_id
            )
            .with_for_update()
            .first()
        )

        if donation is None:
            raise DonationNotFoundException()

        # 6. Confirm that this donation was created for PhonePe.
        payment_method = normalize_status(donation.payment_method)

        if payment_method not in {"PHONEPE", "PHONE_PE"}:
            logger.warning(
                "PhonePe webhook rejected: donation_id=%s, payment_method=%s",
                donation.id,
                payment_method,
            )
            raise InvalidPaymentWebhookException(
                "Donation was not created for PhonePe checkout"
            )

        # 7. Ask PhonePe's server for the authoritative order status.
        try:
            verified = await get_checkout_status(
                merchant_order_id
            )
        except httpx.HTTPError as exc:
            logger.exception(
                "PhonePe order status request failed"
            )
            raise PaymentGatewayUnavailableException() from exc

        if not isinstance(verified, dict):
            raise PaymentGatewayUnavailableException(
                "Invalid response from PhonePe status API"
            )

        verified_order_id = verified.get("merchantOrderId")

        if verified_order_id != merchant_order_id:
            raise InvalidPaymentWebhookException(
                "PhonePe merchant order ID does not match"
            )

        gateway_state = normalize_status(verified.get("state"))

        # 8. Validate the amount before changing payment status.
        verify_amount(
            donation,
            verified.get("amount"),
        )

        current_status = normalize_status(donation.payment_status)

        # Never downgrade a successful donation.
        if current_status == "SUCCESS":
            # Save this event so the same delivery is not processed again.
            db.add(
                PaymentWebhookEvent(
                    event_hash=event_hash,
                    provider="PHONEPE",
                )
            )
            db.commit()

            return {
                "success": True,
                "message": "Donation already verified",
                "payment_status": "SUCCESS",
            }

        # 9. Process only when event and verified gateway state agree.
        if (
            event_type == "checkout.order.completed"
            and gateway_state == "COMPLETED"
        ):
            transaction_reference = (
                get_completed_transaction_reference(verified)
            )

            if not transaction_reference:
                raise PhonePePaymentException(
                    "No completed payment matching the order amount"
                )

            # Prevent one transaction reference from being assigned
            # to multiple donations.
            existing_reference = (
                db.query(Donation)
                .filter(
                    Donation.transaction_reference
                    == transaction_reference,
                    Donation.id != donation.id,
                )
                .first()
            )

            if existing_reference:
                logger.error(
                    "PhonePe transaction reference is already associated "
                    "with another donation; donation_id=%s",
                    donation.id,
                )
                raise PhonePePaymentException(
                    "This transaction reference is already used"
                )

            donation.payment_status = "SUCCESS"
            donation.transaction_reference = transaction_reference

            if hasattr(donation, "verified_at"):
                donation.verified_at = datetime.now(timezone.utc)

        elif (
            event_type == "checkout.order.failed"
            and gateway_state == "FAILED"
        ):
            donation.payment_status = "FAILED"

        else:
            # Pending states and event/status mismatches must not
            # falsely mark a donation successful or failed.
            logger.warning(
                "PhonePe event/status mismatch: event=%s, state=%s, "
                "merchant_order_id=%s",
                event_type,
                gateway_state,
                merchant_order_id,
            )

        # 10. Store event and donation status in the same transaction.
        db.add(
            PaymentWebhookEvent(
                event_hash=event_hash,
                provider="PHONEPE",
            )
        )

        db.commit()
        db.refresh(donation)

        return {
            "success": True,
            "message": "PhonePe webhook processed",
            "payment_status": normalize_status(
                donation.payment_status
            ),
        }

    except IntegrityError as exc:
        db.rollback()

        # A concurrent delivery might have inserted this event first.
        duplicate = (
            db.query(PaymentWebhookEvent)
            .filter(PaymentWebhookEvent.event_hash == event_hash)
            .first()
        )

        if duplicate:
            return {
                "success": True,
                "message": "Duplicate webhook ignored",
            }

        logger.exception(
            "PhonePe webhook database constraint error"
        )
        raise PaymentGatewayUnavailableException() from exc

    except AppException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        logger.exception(
            "Unexpected PhonePe webhook processing error"
        )
        raise PaymentGatewayUnavailableException() from exc
