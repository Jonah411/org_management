from sqlalchemy.orm import Session
import secrets

from src.app.repositories.user_repository import (
    get_user_by_phone
)

from src.app.core.exceptions import (
    UserNotFoundException,
    InvalidOTPException,
    InvalidPasswordException
)

from src.app.services.otp_service import (
    save_otp,
    verify_otp
)

from src.app.core.security import (
    create_access_token,
    verify_password
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
    password = user_data["password"].get_secret_value()

    # =========================
    # CHECK USER
    # =========================

    existing_user = get_user_by_phone(
        db,
        phone_number
    )

    if not existing_user:
        raise UserNotFoundException(
            "Phone number not registered"
        )

    # =========================
    # VERIFY PASSWORD
    # =========================

    if not verify_password(
        password,
        existing_user.password
    ):
        raise InvalidPasswordException(
            "Invalid password"
        )

    # =========================
    # GENERATE OTP
    # =========================

    otp = f"{secrets.randbelow(1_000_000):06d}"

    # =========================
    # SAVE OTP IN REDIS
    # =========================

    save_otp(
        phone_number,
        otp
    )

    # =========================
    # SEND WHATSAPP OTP
    # =========================

    message_sid = send_whatsapp_otp(
        phone_number,
        otp
    )

    # Development only
    print(
        f"OTP for {phone_number}: {otp}"
    )

    return {
        "phone_number": existing_user.phone_number,
        "otp": otp
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
    password = user_data["password"].get_secret_value()

    # =========================
    # CHECK USER
    # =========================

    existing_user = get_user_by_phone(
        db,
        phone_number
    )

    if not existing_user:
        raise UserNotFoundException(
            "Phone number not registered"
        )

    # =========================
    # VERIFY PASSWORD
    # =========================

    if not verify_password(
        password,
        existing_user.password
    ):
        raise InvalidPasswordException(
            "Invalid password"
        )

    # =========================
    # VERIFY OTP
    # =========================

    is_valid = verify_otp(
        phone_number,
        otp
    )

    if not is_valid:
        raise InvalidOTPException(
            "Invalid or expired OTP"
        )

    # =========================
    # CREATE JWT
    # =========================

    access_token = create_access_token(
        existing_user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }