from sqlalchemy.orm import Session
import secrets

from src.app.repositories.user_repository import (
    get_user_by_phone
)

from src.app.core.exceptions import (
    UserNotFoundException,
    InvalidOTPException
)

from src.app.services.otp_service import (
    save_otp,
    verify_otp
)

from src.app.core.security import (
    create_access_token
)

from src.app.services.whatsapp_service import (
    send_whatsapp_otp
)


# =========================
# SEND OTP
# =========================

async def create_login(
    db: Session,
    user_data: dict
):
    phone_number = user_data["phone_number"]

    # Check user exists
    existing_user = get_user_by_phone(
        db,
        phone_number
    )

    if not existing_user:
        raise UserNotFoundException(
            "Phone number not registered"
        )

    # Generate 6 digit OTP
    otp = f"{secrets.randbelow(1_000_000):06d}"

    # Save OTP in Redis
    save_otp(
        phone_number,
        otp
    )

    # Send OTP via SMS
    # await send_otp_sms(
    #     phone_number,
    #     otp
    # )
    message_sid =  send_whatsapp_otp(
    phone_number,
    otp
)

    # Development purpose only
    print(
        f"OTP for {phone_number}: {otp}"
    )

    return {
        "phone_number": existing_user.phone_number,
    }


# =========================
# VERIFY OTP
# =========================

def verify_login(
    db: Session,
    user_data: dict
):
    phone_number = user_data["phone_number"]
    otp = user_data["otp"]

    # Check user exists
    existing_user = get_user_by_phone(
        db,
        phone_number
    )

    if not existing_user:
        raise UserNotFoundException(
            "Phone number not registered"
        )

    # Verify OTP from Redis
    is_valid = verify_otp(
        phone_number,
        otp
    )

    if not is_valid:
        raise InvalidOTPException(
            "Invalid or expired OTP"
        )

    # Generate JWT
    access_token = create_access_token(
        existing_user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }