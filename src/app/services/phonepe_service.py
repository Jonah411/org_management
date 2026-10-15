from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

import httpx

from src.app.core.security import settings


def _base_url() -> str:
    if settings.PHONEPE_ENV.lower() == "production":
        return "https://api.phonepe.com/apis/pg"

    return "https://api-preprod.phonepe.com/apis/pg-sandbox"


def _token_url() -> str:
    if settings.PHONEPE_ENV.lower() == "production":
        return (
            "https://api.phonepe.com/apis/identity-manager"
            "/v1/oauth/token"
        )

    return (
        "https://api-preprod.phonepe.com/apis/pg-sandbox"
        "/v1/oauth/token"
    )


def _require_credentials() -> None:
    required_values = {
        "PHONEPE_CLIENT_ID": settings.PHONEPE_CLIENT_ID,
        "PHONEPE_CLIENT_SECRET": settings.PHONEPE_CLIENT_SECRET,
        "PHONEPE_CLIENT_VERSION": settings.PHONEPE_CLIENT_VERSION,
        "PHONEPE_REDIRECT_URL": settings.PHONEPE_REDIRECT_URL,
    }

    missing = [
        name
        for name, value in required_values.items()
        if value is None or not str(value).strip()
    ]

    if missing:
        raise RuntimeError(
            f"Missing PhonePe configuration: {', '.join(missing)}"
        )


def _get_access_token(client: httpx.Client) -> str:
    _require_credentials()

    response = client.post(
        _token_url(),
        data={
            "client_id": settings.PHONEPE_CLIENT_ID,
            "client_version": settings.PHONEPE_CLIENT_VERSION,
            "client_secret": settings.PHONEPE_CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    response.raise_for_status()

    result = response.json()
    token = result.get("access_token")

    if not token:
        raise RuntimeError(
            "PhonePe did not return an access token"
        )

    return token


def create_checkout(
    donation_id: str,
    amount: Decimal,
) -> dict:
    """
    Donation amount is stored in INR.
    PhonePe checkout amount is sent in paise.
    """

    amount_inr = Decimal(str(amount))

    if amount_inr <= 0:
        raise ValueError(
            "Donation amount must be greater than zero"
        )

    amount_paise = int(
        (amount_inr * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    if amount_paise < 100:
        raise ValueError(
            "PhonePe minimum checkout amount is ₹1"
        )

    merchant_order_id = f"YMCA-{uuid4().hex}"

    with httpx.Client(timeout=20.0) as client:
        token = _get_access_token(client)

        response = client.post(
            f"{_base_url()}/checkout/v2/pay",
            headers={
                "Authorization": f"O-Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "merchantOrderId": merchant_order_id,
                "amount": amount_paise,
                "expireAfter": 1200,
                "paymentFlow": {
                    "type": "PG_CHECKOUT",
                    "message": f"YMCA donation {donation_id}",
                    "merchantUrls": {
                        "redirectUrl": (
                            settings.PHONEPE_REDIRECT_URL
                        ),
                    },
                },
            },
        )

        response.raise_for_status()
        result = response.json()

    redirect_url = result.get("redirectUrl")

    if not redirect_url:
        raise RuntimeError(
            "PhonePe checkout URL is missing from the response"
        )

    return {
        "merchant_order_id": merchant_order_id,
        "phonepe_order_id": result.get("orderId"),
        "state": result.get("state"),
        "redirect_url": redirect_url,
    }


def get_checkout_status(
    merchant_order_id: str,
) -> dict:
    if not merchant_order_id:
        raise ValueError(
            "Merchant order ID is required"
        )

    with httpx.Client(timeout=20.0) as client:
        token = _get_access_token(client)

        response = client.get(
            f"{_base_url()}/checkout/v2/order/"
            f"{merchant_order_id}/status",
            params={
                "details": "true",
            },
            headers={
                "Authorization": f"O-Bearer {token}",
            },
        )

        response.raise_for_status()

        return response.json()
