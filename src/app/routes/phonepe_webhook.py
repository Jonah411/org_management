
import hashlib
import hmac
import json
import logging

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


def verify_phonepe_webhook_auth(
    authorization: str | None,
) -> bool:
    """
    Verify the SHA-256(username:password) format.

    Use this only if this matches the authentication format
    configured for your PhonePe webhook.
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


def normalize_status(value) -> str:
    return str(getattr(value, "value", value)).upper()


def verify_amount(donation: Donation, gateway_amount) -> None:
    """
    Donation amount is assumed to be stored in rupees.
    PhonePe gateway amount is expected in paise.
    """
    if gateway_amount is None:
        raise PhonePePaymentException(
            "Payment amount is missing from gateway response"
        )

    expected_paise = int(round(float(donation.amount) * 100))
    actual_paise = int(gateway_amount)

    if expected_paise != actual_paise:
        raise PhonePePaymentException(
            "Payment amount does not match the donation amount"
        )


@router.post("/phonepe")
async def phonepe_webhook(
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # 1. Authenticate the incoming webhook.
    if not verify_phonepe_webhook_auth(authorization):
        logger.warning(
            "PhonePe webhook authentication failed; header_present=%s",
            bool(authorization),
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid PhonePe webhook authentication",
        )

    # 2. Parse and validate the incoming JSON.
    try:
        raw_body = await request.body()
        body = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise InvalidPaymentWebhookException(
            "Invalid webhook JSON"
        )

    if not isinstance(body, dict):
        raise InvalidPaymentWebhookException(
            "Webhook body must be a JSON object"
        )

    payload = body.get("payload")

    if not isinstance(payload, dict):
        raise InvalidPaymentWebhookException(
            "Webhook payload is missing"
        )

    event_type = body.get("event")
    merchant_order_id = payload.get("merchantOrderId")

    if not event_type or not merchant_order_id:
        raise InvalidPaymentWebhookException(
            "Webhook event or merchant order ID is missing"
        )

    # Ignore events unrelated to payment completion/failure.
    if event_type not in (
        "checkout.order.completed",
        "checkout.order.failed",
    ):
        return {
            "success": True,
            "message": "Webhook event ignored",
        }

    event_hash = hashlib.sha256(raw_body).hexdigest()

    try:
        # 3. Check whether this exact webhook body was processed.
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

        # 4. Lock the donation record.
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

        if normalize_status(donation.payment_method) != "PHONEPE":
            raise InvalidPaymentWebhookException(
                "Donation payment method is not PhonePe"
            )

        # 5. Never trust the webhook payload alone.
        # Verify the order using the PhonePe status API.
        try:
            verified = await get_checkout_status(
                merchant_order_id
            )
        except httpx.HTTPError as exc:
            logger.exception(
                "PhonePe status verification request failed"
            )
            raise PaymentGatewayUnavailableException() from exc

        if not isinstance(verified, dict):
            raise PaymentGatewayUnavailableException(
                "Invalid response from PhonePe status API"
            )

        if verified.get("merchantOrderId") != merchant_order_id:
            raise InvalidPaymentWebhookException(
                "Gateway order ID does not match"
            )

        gateway_state = normalize_status(verified.get("state"))

        # 6. Verify the amount before updating the donation.
        verify_amount(donation, verified.get("amount"))

        # Record this webhook for idempotency.
        db.add(
            PaymentWebhookEvent(
                event_hash=event_hash,
                provider="PHONEPE",
            )
        )

        current_status = normalize_status(donation.payment_status)

        # Never downgrade a successful payment.
        if current_status == "SUCCESS":
            db.commit()
            return {
                "success": True,
                "message": "Donation already verified",
                "payment_status": "SUCCESS",
            }

        # 7. Mark successful only when gateway confirms completion.
        if (
            event_type == "checkout.order.completed"
            and gateway_state == "COMPLETED"
        ):
            payment_details = verified.get("paymentDetails") or []

            if not isinstance(payment_details, list):
                raise InvalidPaymentWebhookException(
                    "Invalid payment details from gateway"
                )

            matching_payment = next(
                (
                    item
                    for item in payment_details
                    if isinstance(item, dict)
                    and normalize_status(item.get("state"))
                    == "COMPLETED"
                    and item.get("amount") is not None
                    and int(item["amount"])
                    == int(verified["amount"])
                ),
                None,
            )

            if matching_payment is None:
                raise PhonePePaymentException(
                    "No completed payment matching the order amount"
                )

            transaction_reference = (
                matching_payment.get("transactionId")
                or verified.get("orderId")
            )

            donation.payment_status = "SUCCESS"
            donation.transaction_reference = transaction_reference

            # Save verification metadata when these model fields exist.
            if hasattr(donation, "verified_at"):
                from datetime import datetime, timezone
                donation.verified_at = datetime.now(timezone.utc)

        elif (
            event_type == "checkout.order.failed"
            and gateway_state == "FAILED"
        ):
            donation.payment_status = "FAILED"

        else:
            # Event and verified gateway state do not agree.
            # Keep the current donation status unchanged.
            logger.warning(
                "PhonePe webhook state mismatch: event=%s state=%s",
                event_type,
                gateway_state,
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

        # A concurrent request may have inserted the same event.
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

        logger.exception("PhonePe webhook database constraint error")
        raise PaymentGatewayUnavailableException() from exc

    except AppException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected PhonePe webhook processing error")
        raise PaymentGatewayUnavailableException() from exc
