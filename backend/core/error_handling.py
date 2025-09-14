"""
Centralized error handling and exception management
Provides consistent error responses and security-aware error handling
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
import uuid

from backend.core.logging_config import security_logger

logger = logging.getLogger(__name__)

class MarketingAIException(Exception):
    """Base exception for Marketing AI platform"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "MARKETING_AI_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class BudgetExceededError(MarketingAIException):
    """Exception for budget-related errors"""
    
    def __init__(self, message: str, current_budget: float, attempted_spend: float):
        super().__init__(
            message,
            error_code="BUDGET_EXCEEDED",
            details={
                "current_budget": current_budget,
                "attempted_spend": attempted_spend,
                "available_budget": max(0, current_budget - attempted_spend)
            }
        )

class AIValidationError(MarketingAIException):
    """Exception for AI validation failures"""
    
    def __init__(self, message: str, risk_level: str, confidence: float, warnings: list):
        super().__init__(
            message,
            error_code="AI_VALIDATION_FAILED",
            details={
                "risk_level": risk_level,
                "confidence": confidence,
                "warnings": warnings
            }
        )

class PrivacyComplianceError(MarketingAIException):
    """Exception for privacy compliance violations"""
    
    def __init__(self, message: str, required_consent: str, user_id: str):
        super().__init__(
            message,
            error_code="PRIVACY_COMPLIANCE_ERROR",
            details={
                "required_consent": required_consent,
                "user_id": user_id
            }
        )

class RateLimitExceededError(MarketingAIException):
    """Exception for rate limit violations"""
    
    def __init__(self, message: str, retry_after: int, limit_type: str):
        super().__init__(
            message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "retry_after_seconds": retry_after,
                "limit_type": limit_type
            }
        )

class ErrorHandler:
    """Centralized error handler for consistent error responses"""
    
    def __init__(self):
        self.error_tracking_enabled = True
    
    def create_error_response(
        self,
        error: Exception,
        request: Request = None,
        user_id: str = None,
        hide_sensitive_details: bool = True
    ) -> JSONResponse:
        """Create standardized error response"""
        
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())
        
        # Base error response
        error_response = {
            "error": True,
            "error_id": error_id,
            "message": "An error occurred",
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat()
        }
        
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Handle specific exception types
        if isinstance(error, BudgetExceededError):
            status_code = status.HTTP_402_PAYMENT_REQUIRED
            error_response.update({
                "message": error.message,
                "error_code": error.error_code,
                "details": error.details if not hide_sensitive_details else {"budget_exceeded": True}
            })
            
            # Log budget violation
            security_logger.log_budget_action(
                user_id or "unknown",
                "budget_exceeded",
                error.details.get("attempted_spend", 0),
                {"error_id": error_id}
            )
        
        elif isinstance(error, AIValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_response.update({
                "message": error.message,
                "error_code": error.error_code,
                "details": {
                    "risk_level": error.details.get("risk_level"),
                    "warnings": error.details.get("warnings", [])[:3]  # Limit warnings
                } if not hide_sensitive_details else {"ai_validation_failed": True}
            })
            
            # Log AI validation failure
            security_logger.log_ai_decision(
                user_id or "unknown",
                "validation_failed",
                error.details.get("confidence", 0),
                error.details.get("risk_level", "unknown")
            )
        
        elif isinstance(error, PrivacyComplianceError):
            status_code = status.HTTP_403_FORBIDDEN
            error_response.update({
                "message": "Privacy consent required",
                "error_code": error.error_code,
                "details": {
                    "required_consent": error.details.get("required_consent"),
                    "consent_url": "/api/v1/privacy/consent"
                }
            })
            
            # Log privacy compliance issue
            security_logger.log_privacy_action(
                user_id or "unknown",
                "consent_violation",
                [error.details.get("required_consent", "unknown")],
                {"error_id": error_id}
            )
        
        elif isinstance(error, RateLimitExceededError):
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            error_response.update({
                "message": error.message,
                "error_code": error.error_code,
                "details": {
                    "retry_after": error.details.get("retry_after_seconds"),
                    "limit_type": error.details.get("limit_type")
                }
            })
        
        elif isinstance(error, RequestValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_response.update({
                "message": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "validation_errors": [
                        {
                            "field": ".".join([str(loc) for loc in err["loc"]]),
                            "message": err["msg"],
                            "type": err["type"]
                        }
                        for err in error.errors()[:5]  # Limit to 5 validation errors
                    ]
                } if not hide_sensitive_details else {"validation_failed": True}
            })
        
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            error_response.update({
                "message": error.detail if not hide_sensitive_details else "Request failed",
                "error_code": "HTTP_ERROR"
            })
        
        else:
            # Generic error handling
            error_response.update({
                "message": "Internal server error" if hide_sensitive_details else str(error),
                "error_code": "INTERNAL_ERROR"
            })
        
        # Log error details
        self._log_error(error, error_id, request, user_id)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    def _log_error(self, error: Exception, error_id: str, request: Request = None, user_id: str = None):
        """Log error details for debugging and monitoring"""
        
        error_details = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "endpoint": f"{request.method} {request.url.path}" if request else None,
            "client_ip": request.client.host if request and request.client else None,
            "user_agent": request.headers.get("user-agent") if request else None
        }
        
        # Include stack trace for internal errors
        if not isinstance(error, (MarketingAIException, HTTPException, RequestValidationError)):
            error_details["stack_trace"] = traceback.format_exc()
        
        # Log based on severity
        if isinstance(error, (BudgetExceededError, PrivacyComplianceError)):
            logger.error(f"Security-related error: {error_details}")
        elif isinstance(error, (AIValidationError, RateLimitExceededError)):
            logger.warning(f"Validation/Rate limit error: {error_details}")
        else:
            logger.error(f"Application error: {error_details}")

# Global error handler instance
error_handler = ErrorHandler()

# Exception handler functions for FastAPI
async def budget_exception_handler(request: Request, exc: BudgetExceededError):
    """Handle budget exceeded exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=False)

async def ai_validation_exception_handler(request: Request, exc: AIValidationError):
    """Handle AI validation exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=False)

async def privacy_exception_handler(request: Request, exc: PrivacyComplianceError):
    """Handle privacy compliance exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=False)

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceededError):
    """Handle rate limit exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=False)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=False)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=True)

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    return error_handler.create_error_response(exc, request, hide_sensitive_details=True)

def setup_error_handlers(app):
    """Setup error handlers for FastAPI application"""
    
    app.add_exception_handler(BudgetExceededError, budget_exception_handler)
    app.add_exception_handler(AIValidationError, ai_validation_exception_handler)
    app.add_exception_handler(PrivacyComplianceError, privacy_exception_handler)
    app.add_exception_handler(RateLimitExceededError, rate_limit_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Error handlers configured successfully")