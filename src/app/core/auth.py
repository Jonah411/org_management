from fastapi import Depends

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import JWTError, jwt

from src.app.core.security import settings

from src.app.core.exceptions import (
    AuthenticationException
)


security = HTTPBearer(
    auto_error=False
)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> int:

    if credentials is None:
        raise AuthenticationException(
            "Authentication credentials are required"
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationException(
                "Invalid token"
            )

        return int(user_id)

    except (JWTError, ValueError):
        raise AuthenticationException(
            "Invalid or expired token"
        )