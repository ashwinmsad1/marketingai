"""
Secure Configuration Manager
Handles environment variable validation, secure defaults, and configuration management
"""

import os
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from urllib.parse import urlparse
import re
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

class ValidationError(ConfigurationError):
    """Custom exception for configuration validation errors"""
    pass

@dataclass
class ConfigValidator:
    """Configuration validator with validation rules"""
    required: bool = False
    default: Optional[Union[str, int, float, bool]] = None
    validator_func: Optional[callable] = None
    description: str = ""
    sensitive: bool = False  # Don't log sensitive values

class SecureConfigManager:
    """
    Secure configuration manager with validation and secure defaults
    """
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self._config_cache: Dict[str, Any] = {}
        self._validators: Dict[str, ConfigValidator] = {}
        self._setup_default_validators()
    
    def _setup_default_validators(self):
        """Setup default configuration validators"""
        
        # API Configuration
        self.register_validator(
            "FACEBOOK_APP_ID",
            ConfigValidator(
                required=True,
                validator_func=self._validate_facebook_app_id,
                description="Facebook App ID for Meta API access",
                sensitive=False
            )
        )
        
        self.register_validator(
            "GOOGLE_API_KEY",
            ConfigValidator(
                required=True,
                validator_func=self._validate_google_api_key,
                description="Google API Key for AI services",
                sensitive=True
            )
        )
        
        self.register_validator(
            "FACEBOOK_APP_SECRET",
            ConfigValidator(
                required=True,
                validator_func=self._validate_facebook_app_secret,
                description="Facebook App Secret for Meta API access",
                sensitive=True
            )
        )
        
        self.register_validator(
            "META_ACCESS_TOKEN",
            ConfigValidator(
                required=True,
                validator_func=self._validate_access_token,
                description="Meta API Access Token",
                sensitive=True
            )
        )
        
        self.register_validator(
            "META_AD_ACCOUNT_ID",
            ConfigValidator(
                required=True,
                validator_func=self._validate_ad_account_id,
                description="Meta Ad Account ID",
                sensitive=False
            )
        )
        
        self.register_validator(
            "FACEBOOK_PAGE_ID",
            ConfigValidator(
                required=True,
                validator_func=self._validate_page_id,
                description="Facebook Page ID",
                sensitive=False
            )
        )
        
        self.register_validator(
            "INSTAGRAM_BUSINESS_ID",
            ConfigValidator(
                required=False,
                validator_func=self._validate_page_id,  # Same validation as page ID
                description="Instagram Business ID",
                sensitive=False
            )
        )
        
        # Redirect URI with secure defaults
        self.register_validator(
            "FACEBOOK_REDIRECT_URI",
            ConfigValidator(
                required=False,
                default="https://localhost:8443/auth/callback",  # HTTPS by default
                validator_func=self._validate_redirect_uri,
                description="OAuth redirect URI (should use HTTPS in production)",
                sensitive=False
            )
        )
        
        # Database Configuration
        self.register_validator(
            "DATABASE_URL",
            ConfigValidator(
                required=False,
                default="postgresql://postgres:password@localhost:5432/ai_marketing_platform",
                validator_func=self._validate_database_url,
                description="Database connection URL",
                sensitive=True
            )
        )
        
        # Security Configuration
        self.register_validator(
            "SECRET_KEY",
            ConfigValidator(
                required=False,
                default=None,  # Will generate if not provided
                validator_func=self._validate_secret_key,
                description="Secret key for cryptographic operations",
                sensitive=True
            )
        )
        
        # Environment Configuration
        self.register_validator(
            "ENVIRONMENT",
            ConfigValidator(
                required=False,
                default="development",
                validator_func=self._validate_environment,
                description="Application environment (development, staging, production)",
                sensitive=False
            )
        )
        
        # Logging Configuration
        self.register_validator(
            "LOG_LEVEL",
            ConfigValidator(
                required=False,
                default="INFO",
                validator_func=self._validate_log_level,
                description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                sensitive=False
            )
        )
        
        # Rate Limiting
        self.register_validator(
            "API_RATE_LIMIT_PER_MINUTE",
            ConfigValidator(
                required=False,
                default="100",
                validator_func=self._validate_positive_integer,
                description="API rate limit per minute",
                sensitive=False
            )
        )
        
        # File Upload Limits
        self.register_validator(
            "MAX_FILE_SIZE_MB",
            ConfigValidator(
                required=False,
                default="50",
                validator_func=self._validate_positive_integer,
                description="Maximum file upload size in MB",
                sensitive=False
            )
        )
        
        # JWT Configuration
        self.register_validator(
            "JWT_ALGORITHM",
            ConfigValidator(
                required=False,
                default="HS256",
                validator_func=self._validate_jwt_algorithm,
                description="JWT signing algorithm",
                sensitive=False
            )
        )
        
        self.register_validator(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            ConfigValidator(
                required=False,
                default="30",
                validator_func=self._validate_positive_integer,
                description="Access token expiration time in minutes",
                sensitive=False
            )
        )
        
        self.register_validator(
            "REFRESH_TOKEN_EXPIRE_DAYS",
            ConfigValidator(
                required=False,
                default="7",
                validator_func=self._validate_positive_integer,
                description="Refresh token expiration time in days",
                sensitive=False
            )
        )
    
    def register_validator(self, key: str, validator: ConfigValidator):
        """Register a configuration validator"""
        self._validators[key] = validator
    
    def get_config(self, key: str, use_cache: bool = True) -> Any:
        """
        Get configuration value with validation
        
        Args:
            key: Configuration key
            use_cache: Whether to use cached values
            
        Returns:
            Validated configuration value
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if use_cache and key in self._config_cache:
            return self._config_cache[key]
        
        validator = self._validators.get(key)
        if not validator:
            # No validator registered, return raw environment variable
            return os.getenv(key)
        
        # Get value from environment
        raw_value = os.getenv(key)
        
        # Handle missing required values
        if validator.required and not raw_value:
            raise ConfigurationError(f"Required configuration '{key}' is missing. {validator.description}")
        
        # Use default if value not provided
        if not raw_value:
            if validator.default is not None:
                value = validator.default
            else:
                value = None
        else:
            value = raw_value
        
        # Apply validation
        if validator.validator_func and value is not None:
            try:
                value = validator.validator_func(value, key)
            except Exception as e:
                raise ValidationError(f"Invalid configuration for '{key}': {e}. {validator.description}")
        
        # Cache the validated value
        self._config_cache[key] = value
        
        # Log configuration (mask sensitive values)
        if not validator.sensitive:
            logger.info(f"Configuration loaded: {key} = {value}")
        else:
            logger.info(f"Configuration loaded: {key} = [REDACTED]")
        
        return value
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all registered configuration values"""
        config = {}
        for key in self._validators:
            try:
                config[key] = self.get_config(key)
            except ConfigurationError as e:
                logger.error(f"Failed to load config {key}: {e}")
                config[key] = None
        return config
    
    def validate_all_config(self) -> Dict[str, Any]:
        """Validate all configuration and return results"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config': {}
        }
        
        for key in self._validators:
            try:
                value = self.get_config(key, use_cache=False)  # Force revalidation
                results['config'][key] = value
            except ConfigurationError as e:
                results['valid'] = False
                results['errors'].append(f"{key}: {e}")
                logger.error(f"Configuration validation failed for {key}: {e}")
        
        # Add warnings for insecure configurations
        environment = results['config'].get('ENVIRONMENT', 'development')
        if environment == 'production':
            redirect_uri = results['config'].get('FACEBOOK_REDIRECT_URI', '')
            if redirect_uri and not redirect_uri.startswith('https://'):
                results['warnings'].append("FACEBOOK_REDIRECT_URI should use HTTPS in production")
        
        return results
    
    # Validation Functions
    def _validate_facebook_app_id(self, value: str, key: str) -> str:
        """Validate Facebook App ID"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Facebook App ID cannot be empty")
        
        if not re.match(r'^\d+$', value):
            raise ValueError("Facebook App ID must contain only digits")
        
        if len(value) < 15 or len(value) > 20:
            raise ValueError("Facebook App ID must be 15-20 digits long")
        
        return value
    
    def _validate_facebook_app_secret(self, value: str, key: str) -> str:
        """Validate Facebook App Secret"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Facebook App Secret cannot be empty")
        
        if len(value) != 32:
            raise ValueError("Facebook App Secret must be exactly 32 characters long")
        
        if not re.match(r'^[a-f0-9]+$', value):
            raise ValueError("Facebook App Secret must contain only lowercase hex characters")
        
        return value
    
    def _validate_access_token(self, value: str, key: str) -> str:
        """Validate Meta API Access Token"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Access token cannot be empty")
        
        if len(value) < 50:
            raise ValueError("Access token appears to be too short")
        
        # Basic format validation for Meta tokens
        if not any(char.isalnum() for char in value):
            raise ValueError("Access token must contain alphanumeric characters")
        
        return value
    
    def _validate_google_api_key(self, value: str, key: str) -> str:
        """Validate Google API Key"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Google API Key cannot be empty")
        
        # Google API keys typically start with "AIza" and are 39 characters long
        if not value.startswith("AIza"):
            raise ValueError("Google API Key must start with 'AIza'")
        
        if len(value) != 39:
            raise ValueError("Google API Key must be 39 characters long")
        
        # Basic format validation
        if not re.match(r'^AIza[A-Za-z0-9_-]+$', value):
            raise ValueError("Google API Key contains invalid characters")
        
        return value
    
    def _validate_ad_account_id(self, value: str, key: str) -> str:
        """Validate Meta Ad Account ID"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Ad Account ID cannot be empty")
        
        # Remove 'act_' prefix if present
        if value.startswith('act_'):
            value = value[4:]
        
        if not re.match(r'^\d+$', value):
            raise ValueError("Ad Account ID must contain only digits")
        
        return value
    
    def _validate_page_id(self, value: str, key: str) -> str:
        """Validate Facebook Page ID"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Page ID cannot be empty")
        
        if not re.match(r'^\d+$', value):
            raise ValueError("Page ID must contain only digits")
        
        return value
    
    def _validate_redirect_uri(self, value: str, key: str) -> str:
        """Validate OAuth redirect URI"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Redirect URI cannot be empty")
        
        # Parse URL
        try:
            parsed = urlparse(value)
        except Exception:
            raise ValueError("Invalid URL format")
        
        if not parsed.scheme:
            raise ValueError("Redirect URI must include protocol (http/https)")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Redirect URI must use http or https protocol")
        
        if not parsed.netloc:
            raise ValueError("Redirect URI must include hostname")
        
        # Warn about insecure configurations in production
        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'production' and parsed.scheme == 'http':
            logger.warning("Using HTTP redirect URI in production is not recommended")
        
        return value
    
    def _validate_database_url(self, value: str, key: str) -> str:
        """Validate database URL"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not value:
            raise ValueError("Database URL cannot be empty")
        
        # Basic URL validation
        if '://' not in value:
            raise ValueError("Database URL must include protocol")
        
        return value
    
    def _validate_secret_key(self, value: Optional[str], key: str) -> str:
        """Validate secret key"""
        if value is None:
            # Generate secure random key
            import secrets
            value = secrets.token_hex(32)
            logger.warning(f"Generated random secret key for {key}. Consider setting this explicitly.")
        
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if len(value) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        return value
    
    def _validate_environment(self, value: str, key: str) -> str:
        """Validate environment setting"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip().lower()
        
        valid_environments = ['development', 'staging', 'production', 'test']
        if value not in valid_environments:
            raise ValueError(f"Environment must be one of: {', '.join(valid_environments)}")
        
        return value
    
    def _validate_log_level(self, value: str, key: str) -> str:
        """Validate log level"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip().upper()
        
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if value not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        
        return value
    
    def _validate_positive_integer(self, value: Union[str, int], key: str) -> int:
        """Validate positive integer"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValueError("Must be a valid integer")
        
        if int_value <= 0:
            raise ValueError("Must be a positive integer")
        
        return int_value
    
    def _validate_jwt_algorithm(self, value: str, key: str) -> str:
        """Validate JWT algorithm"""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip().upper()
        
        valid_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'ES512']
        if value not in valid_algorithms:
            raise ValueError(f"JWT algorithm must be one of: {', '.join(valid_algorithms)}")
        
        return value

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> SecureConfigManager:
    """Get or create global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager

# Convenience functions
def get_config(key: str, use_cache: bool = True) -> Any:
    """Get configuration value"""
    return get_config_manager().get_config(key, use_cache)

def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration"""
    return get_config_manager().validate_all_config()

def is_production() -> bool:
    """Check if running in production environment"""
    return get_config('ENVIRONMENT', use_cache=True) == 'production'

def is_development() -> bool:
    """Check if running in development environment"""
    return get_config('ENVIRONMENT', use_cache=True) == 'development'

# Example usage and testing
def test_config_manager():
    """Test configuration manager functionality"""
    print("🔧 Testing Secure Configuration Manager...")
    
    manager = SecureConfigManager()
    
    # Test validation
    validation_results = manager.validate_all_config()
    
    print(f"✅ Configuration validation: {'PASSED' if validation_results['valid'] else 'FAILED'}")
    
    if validation_results['errors']:
        print("❌ Errors found:")
        for error in validation_results['errors']:
            print(f"  - {error}")
    
    if validation_results['warnings']:
        print("⚠️  Warnings:")
        for warning in validation_results['warnings']:
            print(f"  - {warning}")
    
    print("🎉 Configuration manager tests completed!")

if __name__ == "__main__":
    test_config_manager()