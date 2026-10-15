from typing import Any


class AppException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self,
        message: str = "An application error occurred",
        status_code: int = 500,
        error_code: str = "APP_ERROR",
        details: Any = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

        super().__init__(message)


# =========================================================
# USER EXCEPTIONS
# =========================================================

class UserNotFoundException(AppException):
    def __init__(
        self,
        message: str = "User not found",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="USER_NOT_FOUND",
            details=details,
        )


class UserAlreadyExistsException(AppException):
    def __init__(
        self,
        message: str = "User already exists",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
            details=details,
        )


# =========================================================
# AUTHENTICATION EXCEPTIONS
# =========================================================

class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication required",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "You are not authorized to perform this action",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class InvalidOTPException(AppException):
    def __init__(
        self,
        message: str = "Invalid or expired OTP",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_OTP",
            details=details,
        )


class InvalidPasswordException(AppException):
    def __init__(
        self,
        message: str = "Invalid password",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_PASSWORD",
            details=details,
        )


# =========================================================
# AI SERVICE EXCEPTIONS
# =========================================================

class AIServiceException(AppException):
    def __init__(
        self,
        message: str = "AI service operation failed",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=502,
            error_code="AI_SERVICE_ERROR",
            details=details,
        )


# =========================================================
# DONATION TYPE EXCEPTIONS
# =========================================================

class DonationTypeNotFoundException(AppException):
    def __init__(
        self,
        message: str = "Donation type not found",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="DONATION_TYPE_NOT_FOUND",
            details=details,
        )


class DonationTypeAlreadyExistsException(AppException):
    def __init__(
        self,
        message: str = "Donation type already exists",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code="DONATION_TYPE_ALREADY_EXISTS",
            details=details,
        )


class DonationTypeInactiveException(AppException):
    def __init__(
        self,
        message: str = "Donation type is inactive",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="DONATION_TYPE_INACTIVE",
            details=details,
        )


class DonationTypeValidationException(AppException):
    def __init__(
        self,
        message: str = "Invalid donation type data",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=422,
            error_code="DONATION_TYPE_VALIDATION_ERROR",
            details=details,
        )


# =========================================================
# DONATION EXCEPTIONS
# =========================================================

class DonationNotFoundException(AppException):
    def __init__(
        self,
        message: str = "Donation not found",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="DONATION_NOT_FOUND",
            details=details,
        )


class InvalidDonationException(AppException):
    def __init__(
        self,
        message: str = "Invalid donation request",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_DONATION",
            details=details,
        )


# =========================================================
# UPI PAYMENT EXCEPTIONS
# =========================================================

class UPIConfigurationException(AppException):
    def __init__(
        self,
        message: str = "UPI payment configuration is missing",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="UPI_CONFIGURATION_ERROR",
            details=details,
        )


class UPIQRNotAvailableException(AppException):
    def __init__(
        self,
        message: str = "UPI QR is not available for this donation",
        details: Any = None,
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="UPI_QR_NOT_AVAILABLE",
            details=details,
        )


class InactiveDonationTypeException(AppException):
    def __init__(
        self,
        message: str = "This donation type is inactive",
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="DONATION_TYPE_INACTIVE",
        )


class PhonePeWebhookAuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Invalid PhonePe webhook authentication",
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="PHONEPE_WEBHOOK_AUTHENTICATION_FAILED",
        )


class PhonePePaymentException(AppException):
    def __init__(
        self,
        message: str = "PhonePe payment verification failed",
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="PHONEPE_PAYMENT_VERIFICATION_FAILED",
        )


class PaymentEventConflictException(AppException):
    def __init__(
        self,
        message: str = "Payment event conflicts with the current status",
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code="PAYMENT_EVENT_CONFLICT",
        )


class PaymentGatewayUnavailableException(AppException):
    def __init__(
        self,
        message: str = "Payment gateway is temporarily unavailable",
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_code="PAYMENT_GATEWAY_UNAVAILABLE",
        )
class InvalidPaymentWebhookException(AppException):
    def __init__(
        self,
        message: str = "Invalid payment webhook payload",
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_PAYMENT_WEBHOOK",
        )