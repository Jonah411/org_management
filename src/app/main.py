
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# --------------------------------------------------
# Routes
# --------------------------------------------------

from src.app.routes.user_routes import router as user_router
from src.app.routes.login_routes import router as login_router
from src.app.routes.role_routes import router as role_router
from src.app.routes.donation_type import router as donation_type_router
from src.app.routes.donation import router as donation_router
from src.app.routes.donation_payment_routes import router as donation_payment_router
from src.app.routes.phonepe_webhook import router as phonepe_webhook_router

# AI routes
# from src.app.routes.ai_routes import router as ai_router
# from src.app.routes.ai_analysis_routes import router as ai_analysis_router
# from src.app.routes.ai import router as ai_router
# from src.app.routes.user_ai import router as user_ai_router
# from src.app.routes.business_ai import router as business_ai_router


# --------------------------------------------------
# Middleware
# --------------------------------------------------

from src.app.middleware.logging_middleware import logging_middleware


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

from src.app.core.exception_handlers import (
    validation_exception_handler,
    user_not_found_exception_handler,
    user_already_exists_handler,
    invalid_otp_exception_handler,
    internal_server_exception_handler,
    authentication_exception_handler,
    invalid_password_exception_handler,
    donation_type_not_found_handler,
    donation_type_already_exists_handler,
    donation_type_inactive_handler,
    donation_type_validation_handler,
    invalid_donation_exception_handler,
    upi_configuration_exception_handler,
    upi_qr_not_available_handler,
    app_exception_handler,
)


# --------------------------------------------------
# Custom Exceptions
# --------------------------------------------------

from src.app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidOTPException,
    AuthenticationException,
    InvalidPasswordException,
    DonationTypeNotFoundException,
    DonationTypeAlreadyExistsException,
    DonationTypeInactiveException,
    DonationTypeValidationException,
    InvalidDonationException,
    UPIConfigurationException,
    UPIQRNotAvailableException,
)


# --------------------------------------------------
# Database
# --------------------------------------------------

from src.app.core.database import Base, engine


# IMPORTANT:
# Import ALL SQLAlchemy models before create_all().
# This registers the models with Base.metadata.

from src.app.models.user_model import User
from src.app.models.role_model import Role


# --------------------------------------------------
# Create Database Tables
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Org YMCA API",
    version="1.0.0",
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------

app.middleware("http")(logging_middleware)


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    UserNotFoundException,
    user_not_found_exception_handler,
)

app.add_exception_handler(
    UserAlreadyExistsException,
    user_already_exists_handler,
)

app.add_exception_handler(
    InvalidOTPException,
    invalid_otp_exception_handler,
)

app.add_exception_handler(
    AuthenticationException,
    authentication_exception_handler,
)

app.add_exception_handler(
    Exception,
    internal_server_exception_handler,
)

app.add_exception_handler(
    InvalidPasswordException,
    invalid_password_exception_handler,
)

app.add_exception_handler(
    DonationTypeNotFoundException,
    donation_type_not_found_handler,
)

app.add_exception_handler(
    DonationTypeAlreadyExistsException,
    donation_type_already_exists_handler,
)

app.add_exception_handler(
    DonationTypeInactiveException,
    donation_type_inactive_handler,
)

app.add_exception_handler(
    DonationTypeValidationException,
    donation_type_validation_handler,
)
app.add_exception_handler(
    InvalidDonationException,
    invalid_donation_exception_handler,
)

# UPI
app.add_exception_handler(
    UPIConfigurationException,
    upi_configuration_exception_handler,
)
app.add_exception_handler(
    UPIQRNotAvailableException,
    upi_qr_not_available_handler,
)

# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(user_router)
app.include_router(login_router)
app.include_router(role_router)
app.include_router(donation_type_router)
app.include_router(donation_router)
app.include_router(donation_payment_router)
app.include_router(phonepe_webhook_router)


# --------------------------------------------------
# AI Routes
# --------------------------------------------------

# app.include_router(ai_router)
# app.include_router(ai_analysis_router)
# app.include_router(user_ai_router)
# app.include_router(business_ai_router)
# Register the donation router with your existing routers

