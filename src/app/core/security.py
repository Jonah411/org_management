from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from twilio.rest import Client

from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    InvalidHashError,
)


# ============================================================
# PASSWORD HASHER
# ============================================================

password_hasher = PasswordHasher()


# ============================================================
# SETTINGS
# ============================================================

class Settings(BaseSettings):

    # ========================================================
    # JWT
    # ========================================================

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ========================================================
    # TWILIO
    # ========================================================

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_FROM: str
    TWILIO_WHATSAPP_TEMPLATE_SID: str

    # ========================================================
    # OPENAI
    # ========================================================

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ========================================================
    # CONFIG
    # ========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()


# ============================================================
# JWT
# ============================================================

def create_access_token(
    user_id: int,
) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ============================================================
# TWILIO
# ============================================================

def get_twilio_client() -> Client:

    return Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )


def get_whatsapp_from() -> str:

    return settings.TWILIO_WHATSAPP_FROM


def get_whatsapp_template_sid() -> str:

    return settings.TWILIO_WHATSAPP_TEMPLATE_SID


# ============================================================
# PASSWORD
# ============================================================

def hash_password(
    password: str,
) -> str:

    return password_hasher.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    try:

        return password_hasher.verify(
            hashed_password,
            plain_password,
        )

    except (
        VerifyMismatchError,
        InvalidHashError,
    ):

        return False