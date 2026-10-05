from secrets import randbelow

from src.app.core.redis import redis_client


OTP_EXPIRY_SECONDS = 60


def generate_otp() -> str:
    return f"{randbelow(1_000_000):06d}"


def save_otp(
    phone_number: str,
    otp: str
) -> None:

    redis_key = f"otp:{phone_number}"

    redis_client.set(
        redis_key,
        otp,
        ex=OTP_EXPIRY_SECONDS
    )


def get_otp(
    phone_number: str
) -> str | None:

    redis_key = f"otp:{phone_number}"

    return redis_client.get(
        redis_key
    )


def delete_otp(
    phone_number: str
) -> None:

    redis_key = f"otp:{phone_number}"

    redis_client.delete(
        redis_key
    )


def verify_otp(
    phone_number: str,
    otp: str
) -> bool:

    stored_otp = get_otp(
        phone_number
    )

    if stored_otp is None:
        return False

    if stored_otp != otp:
        return False

    # OTP can be used only once
    delete_otp(
        phone_number
    )

    return True