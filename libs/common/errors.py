"""
Standard error types for WaqediAI services.

All custom exceptions inherit from WaqediError, enabling
consistent error handling and RFC 7807 Problem Details responses.
"""

from typing import Any


class WaqediError(Exception):
    """
    Base exception for all WaqediAI errors.

    Attributes:
        message: Human-readable error description.
        error_code: Machine-readable error code (e.g., "DOCUMENT_NOT_FOUND").
        status_code: HTTP status code for API responses.
        details: Additional error context.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_problem_details(self) -> dict[str, Any]:
        """
        Convert to RFC 7807 Problem Details format.

        Returns:
            Dictionary conforming to Problem Details specification.
        """
        return {
            "type": f"urn:waqedi:error:{self.error_code.lower().replace('_', '-')}",
            "title": self.error_code.replace("_", " ").title(),
            "status": self.status_code,
            "detail": self.message,
            **self.details,
        }


class ValidationError(WaqediError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(WaqediError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
    ) -> None:
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class AuthorizationError(WaqediError):
    """Raised when user is not authorized to perform an action."""

    def __init__(
        self,
        message: str = "Not authorized to perform this action",
        required_permission: str | None = None,
    ) -> None:
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class AuthenticationError(WaqediError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication required",
    ) -> None:
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class ServiceUnavailableError(WaqediError):
    """Raised when a dependent service is unavailable."""

    def __init__(
        self,
        service_name: str,
        reason: str | None = None,
    ) -> None:
        message = f"Service '{service_name}' is currently unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"service": service_name},
        )


class RateLimitError(WaqediError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        retry_after: int | None = None,
    ) -> None:
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message="Rate limit exceeded. Please retry later.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


class ConflictError(WaqediError):
    """Raised when there's a resource conflict (e.g., duplicate)."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
    ) -> None:
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )
