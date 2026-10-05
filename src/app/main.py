from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.app.routes.user_routes import router as user_router
from src.app.routes.login_routes import router as login_router

from src.app.middleware.logging_middleware import logging_middleware

from src.app.core.exception_handlers import (
    validation_exception_handler,
    user_not_found_exception_handler,
    user_already_exists_handler,
    invalid_otp_exception_handler,
    internal_server_exception_handler,
    authentication_exception_handler
)

from src.app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidOTPException,
    AuthenticationException
)

from src.app.core.database import Base, engine
from src.app.models.user_model import User


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Org YMCA API",
    version="1.0.0"
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------

app.middleware("http")(logging_middleware)


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

# Pydantic validation errors
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)


# User not found
app.add_exception_handler(
    UserNotFoundException,
    user_not_found_exception_handler
)


# User already exists
app.add_exception_handler(
    UserAlreadyExistsException,
    user_already_exists_handler
)

app.add_exception_handler(
    InvalidOTPException,
    invalid_otp_exception_handler
)

app.add_exception_handler(
    AuthenticationException,
    authentication_exception_handler
)

# Generic / unexpected errors
app.add_exception_handler(
    Exception,
    internal_server_exception_handler
)


# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(user_router)
app.include_router(login_router)