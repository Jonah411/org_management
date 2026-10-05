import httpx

from src.app.core.security import settings


async def send_otp_sms(
    phone_number: str,
    otp: str
):
    url = "https://control.msg91.com/api/v5/otp"

    params = {
        "template_id": settings.MSG91_OTP_TEMPLATE_ID,
        "mobile": f"91{phone_number}",
        "authkey": settings.MSG91_AUTH_KEY,
        "otp": otp,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            params=params
        )

    response.raise_for_status()

    return response.json()