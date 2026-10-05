from fastapi import Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidOTPException,
    AuthenticationException,
)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    request_id = request.state.request_id

    errors = []

    for error in exc.errors():

        location = error.get("loc", [])

        field = ".".join(
            str(item)
            for item in location
            if item != "body"
        )

        errors.append({
            "field": field or "body",
            "message": error.get("msg"),
            "type": error.get("type")
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "request_id": request_id,
            "errors": errors
        }
    )


async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundException
):
    request_id = request.state.request_id

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": exc.message,
            "error_code": "USER_NOT_FOUND",
            "request_id": request_id
        }
    )


async def internal_server_exception_handler(
    request: Request,
    exc: Exception
):
    request_id = request.state.request_id

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Something went wrong",
            "error_code": "INTERNAL_SERVER_ERROR",
            "request_id": request_id
        }
    )

async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsException
):
    request_id = request.state.request_id

    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": exc.message,
            "error_code": "USER_ALREADY_EXISTS",
            "request_id": request_id
        }
    )

async def invalid_otp_exception_handler(
    request: Request,
    exc: InvalidOTPException
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.message,
            "error_code": "INVALID_OTP",
            "request_id": request.state.request_id
        }
    )

async def authentication_exception_handler(
    request: Request,
    exc: AuthenticationException
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.message,
            "error_code": "AUTHENTICATION_FAILED",
            "request_id": request.state.request_id
        }
    )