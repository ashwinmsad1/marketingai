"""
Centralized logging configuration for the marketing automation platform
Provides structured logging, error tracking, and audit trails
"""
import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any
import json
import os

class SecurityAuditLogger:
    """Specialized logger for security and compliance events"""
    
    def __init__(self, name: str = "security_audit"):
        self.logger = logging.getLogger(name)
        self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Configure security audit logger with special handling"""
        if not self.logger.handlers:
            # Create file handler for security logs
            audit_file = "logs/security_audit.log"
            os.makedirs(os.path.dirname(audit_file), exist_ok=True)
            
            handler = logging.FileHandler(audit_file)
            handler.setLevel(logging.INFO)
            
            # Security log format includes more details
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_budget_action(self, user_id: str, action: str, amount: float, details: Dict[str, Any]):
        """Log budget-related actions for compliance"""
        self.logger.info(f"BUDGET_ACTION | User: {user_id} | Action: {action} | Amount: ${amount} | Details: {json.dumps(details)}")
    
    def log_ai_decision(self, user_id: str, prediction_type: str, confidence: float, risk_level: str):
        """Log AI decisions for audit trail"""
        self.logger.info(f"AI_DECISION | User: {user_id} | Type: {prediction_type} | Confidence: {confidence} | Risk: {risk_level}")
    
    def log_privacy_action(self, user_id: str, action: str, data_types: list, details: Dict[str, Any]):
        """Log privacy-related actions (GDPR compliance)"""
        self.logger.info(f"PRIVACY_ACTION | User: {user_id} | Action: {action} | DataTypes: {data_types} | Details: {json.dumps(details)}")
    
    def log_failed_auth(self, user_id: str, ip_address: str, reason: str):
        """Log failed authentication attempts"""
        self.logger.warning(f"AUTH_FAILED | User: {user_id} | IP: {ip_address} | Reason: {reason}")

def setup_logging(environment: str = "development") -> Dict[str, Any]:
    """
    Setup centralized logging configuration
    
    Args:
        environment: Environment name (development, staging, production)
    
    Returns:
        Logging configuration dictionary
    """
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Base logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s | %(name)s | %(message)s"
            },
            "json": {
                "()": JsonFormatter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO" if environment == "production" else "DEBUG",
                "formatter": "simple",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/application.log",
                "mode": "a"
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed", 
                "filename": "logs/error.log",
                "mode": "a"
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": "DEBUG" if environment != "production" else "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if environment == "production" else "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "security_audit": {
                "level": "INFO",
                "handlers": ["file", "error_file"],
                "propagate": False
            }
        }
    }
    
    # Production-specific settings
    if environment == "production":
        # Add rotation for production logs
        config["handlers"]["file"]["class"] = "logging.handlers.RotatingFileHandler"
        config["handlers"]["file"]["maxBytes"] = 10 * 1024 * 1024  # 10MB
        config["handlers"]["file"]["backupCount"] = 5
        
        config["handlers"]["error_file"]["class"] = "logging.handlers.RotatingFileHandler"
        config["handlers"]["error_file"]["maxBytes"] = 10 * 1024 * 1024  # 10MB
        config["handlers"]["error_file"]["backupCount"] = 5
        
        # JSON format for production (better for log aggregation)
        config["formatters"]["production"] = {
            "()": JsonFormatter
        }
        config["handlers"]["file"]["formatter"] = "production"
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    return config

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
            
        return json.dumps(log_entry)

class PerformanceLogger:
    """Logger for performance monitoring and bottleneck detection"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_slow_query(self, query: str, execution_time: float, user_id: str = None):
        """Log slow database queries for optimization"""
        if execution_time > 1.0:  # Log queries slower than 1 second
            self.logger.warning(
                f"SLOW_QUERY | Time: {execution_time:.2f}s | User: {user_id} | Query: {query[:200]}..."
            )
    
    def log_api_performance(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API endpoint performance"""
        if response_time > 2.0:  # Log slow API responses
            self.logger.warning(
                f"SLOW_API | Endpoint: {method} {endpoint} | Time: {response_time:.2f}s | Status: {status_code}"
            )
    
    def log_ml_prediction_time(self, prediction_type: str, processing_time: float, user_id: str):
        """Log ML prediction processing times"""
        self.logger.info(
            f"ML_PREDICTION | Type: {prediction_type} | Time: {processing_time:.2f}s | User: {user_id}"
        )

# Global logger instances
security_logger = SecurityAuditLogger()
performance_logger = PerformanceLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)

def log_request_context(logger: logging.Logger, user_id: str = None, request_id: str = None, ip_address: str = None):
    """Add context information to log records"""
    class ContextFilter(logging.Filter):
        def filter(self, record):
            if user_id:
                record.user_id = user_id
            if request_id:
                record.request_id = request_id
            if ip_address:
                record.ip_address = ip_address
            return True
    
    logger.addFilter(ContextFilter())