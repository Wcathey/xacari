from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import XacariException
from app.core.logging import logger, log_with_context
import traceback
from typing import Union


async def xacari_exception_handler(request: Request, exc: XacariException) -> JSONResponse:
    """
    Handler for custom Xacari exceptions.
    """
    log_with_context(
        logger,
        "warning",
        f"Xacari exception: {exc.message}",
        path=request.url.path,
        status_code=exc.status_code,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions.
    """
    log_with_context(
        logger,
        "warning",
        f"HTTP exception: {exc.detail}",
        path=request.url.path,
        status_code=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "type": "HTTPException",
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.
    """
    errors = exc.errors()

    log_with_context(
        logger,
        "warning",
        "Validation error",
        path=request.url.path,
        errors=errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": errors,
            "type": "ValidationError",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for all unhandled exceptions.
    """
    tb = traceback.format_exc()

    log_with_context(
        logger,
        "error",
        f"Unhandled exception: {str(exc)}",
        path=request.url.path,
        exception_type=exc.__class__.__name__,
        traceback=tb,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "type": "InternalServerError",
        },
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI app.
    """
    app.add_exception_handler(XacariException, xacari_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
