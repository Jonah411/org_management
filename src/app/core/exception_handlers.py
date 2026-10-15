from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.app.core.exceptions import (
    AppException,
    InvalidPasswordException,
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidOTPException,
    AuthenticationException,
    AuthorizationException,
    AIServiceException,
    DonationNotFoundException,
    DonationTypeNotFoundException,
    DonationTypeAlreadyExistsException,
    DonationTypeInactiveException,
    DonationTypeValidationException,
    InvalidDonationException,
    UPIConfigurationException,
    UPIQRNotAvailableException,
    PaymentEventConflictException
)


# =========================================================
# COMMON HELPER
# =========================================================

def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def create_error_response(
    request: Request,
    message: str,
    error_code: str,
    status_code: int,
    details=None,
) -> JSONResponse:
    content = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "request_id": get_request_id(request),
    }

    if details is not None:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


# =========================================================
# REQUEST VALIDATION EXCEPTION
# =========================================================

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        location = error.get("loc", [])

        field = ".".join(
            str(item)
            for item in location
            if item != "body"
        )

        errors.append(
            {
                "field": field or "body",
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error"),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "request_id": get_request_id(request),
            "errors": errors,
        },
    )


# =========================================================
# USER EXCEPTIONS
# =========================================================

async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# AUTHENTICATION EXCEPTIONS
# =========================================================

async def authentication_exception_handler(
    request: Request,
    exc: AuthenticationException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def authorization_exception_handler(
    request: Request,
    exc: AuthorizationException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def invalid_otp_exception_handler(
    request: Request,
    exc: InvalidOTPException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def invalid_password_exception_handler(
    request: Request,
    exc: InvalidPasswordException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# AI SERVICE EXCEPTION
# =========================================================

async def ai_service_exception_handler(
    request: Request,
    exc: AIServiceException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# DONATION TYPE EXCEPTIONS
# =========================================================

async def donation_type_not_found_handler(
    request: Request,
    exc: DonationTypeNotFoundException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def donation_type_already_exists_handler(
    request: Request,
    exc: DonationTypeAlreadyExistsException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def donation_type_inactive_handler(
    request: Request,
    exc: DonationTypeInactiveException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def donation_type_validation_handler(
    request: Request,
    exc: DonationTypeValidationException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# DONATION EXCEPTIONS
# =========================================================

async def donation_not_found_handler(
    request: Request,
    exc: DonationNotFoundException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def invalid_donation_exception_handler(
    request: Request,
    exc: InvalidDonationException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# UPI PAYMENT EXCEPTIONS
# =========================================================

async def upi_configuration_exception_handler(
    request: Request,
    exc: UPIConfigurationException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


async def upi_qr_not_available_handler(
    request: Request,
    exc: UPIQRNotAvailableException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# GENERIC APPLICATION EXCEPTION
# =========================================================

async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return create_error_response(
        request=request,
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details,
    )


# =========================================================
# UNEXPECTED INTERNAL SERVER ERROR
# =========================================================

async def internal_server_exception_handler(
    request: Request,
    exc: Exception,
):
    # Log the full exception on the server using your
    # application's configured logger.
    # Do not expose internal exception details to clients.

    return create_error_response(
        request=request,
        message="Something went wrong",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

async def payment_event_conflict_handler(
    request: Request,
    exc: PaymentEventConflictException,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": str(exc),
            "data": None,
            "request_id": getattr(request.state, "request_id", None),
        },
    )