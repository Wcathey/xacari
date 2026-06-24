from typing import Any, Optional
from fastapi import HTTPException, status


class XacariException(Exception):
    """Base exception for Xacari application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class WorkoutSessionException(XacariException):
    """Exception raised for workout session errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class PoseAnalysisException(XacariException):
    """Exception raised for pose analysis errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class WebSocketException(XacariException):
    """Exception raised for WebSocket errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ConfigurationException(XacariException):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class AuthenticationException(XacariException):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationException(XacariException):
    """Exception raised for authorization errors."""

    def __init__(self, message: str = "Access denied", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ResourceNotFoundException(XacariException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: str, details: Optional[dict[str, Any]] = None):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )
