"""
Custom exceptions for the AI Marketing Automation Platform
Consolidated exception handling - imports from error_handling.py
"""

# Import comprehensive exception classes from error_handling module
from backend.core.error_handling import (
    MarketingAIException,
    BudgetExceededError,
    AIValidationError,
    PrivacyComplianceError,
    RateLimitExceededError,
    ErrorHandler,
    error_handler
)

# Legacy exception classes for backward compatibility
class AuthenticationError(MarketingAIException):
    """Authentication related errors"""
    pass


class AuthorizationError(MarketingAIException):
    """Authorization related errors"""
    pass


class ValidationError(MarketingAIException):
    """Validation related errors"""
    pass


class ExternalServiceError(MarketingAIException):
    """External service integration errors"""
    pass


class AIServiceError(ExternalServiceError):
    """AI service specific errors"""
    pass


class MetaAPIError(ExternalServiceError):
    """Meta/Facebook API specific errors"""
    pass


class PaymentError(ExternalServiceError):
    """Payment processing errors"""
    pass


class BudgetValidationError(ValidationError):
    """Budget validation and safety control errors - use BudgetExceededError for new code"""
    pass


class InsufficientFundsError(BudgetValidationError):
    """Insufficient funds or balance errors"""
    pass


class BudgetLimitExceededError(BudgetValidationError):
    """Budget limit exceeded errors - use BudgetExceededError for new code"""
    pass


class RateLimitError(MarketingAIException):
    """Rate limiting errors - use RateLimitExceededError for new code"""
    pass


# HTTP Exception shortcuts - maintained for backward compatibility
from fastapi import HTTPException, status


def unauthorized_exception(detail: str = "Authentication required"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(detail: str = "Not enough permissions"):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def not_found_exception(detail: str = "Resource not found"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def validation_exception(detail: str = "Validation error"):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )


def server_error_exception(detail: str = "Internal server error"):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    )


def budget_exceeded_exception(detail: str = "Budget limit exceeded"):
    return HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=detail
    )


def insufficient_funds_exception(detail: str = "Insufficient funds"):
    return HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=detail
    )


def rate_limit_exception(detail: str = "Rate limit exceeded", retry_after: int = 60):
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
        headers={"Retry-After": str(retry_after)}
    )