"""
Centralized Meta API configuration management
Provides consistent configuration access across all Meta integrations
"""
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .config_manager import get_config, ConfigurationError

logger = logging.getLogger(__name__)


class MetaEnvironment(Enum):
    """Meta API environments"""
    PRODUCTION = "production"
    DEVELOPMENT = "development" 
    TESTING = "testing"


@dataclass
class MetaAPIConfig:
    """Configuration class for Meta API settings"""
    
    # Core Authentication
    access_token: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    
    # Account IDs
    facebook_page_id: Optional[str] = None
    instagram_business_id: Optional[str] = None
    ad_account_id: Optional[str] = None
    
    # API Configuration
    api_version: str = "v21.0"
    graph_api_version: str = "v21.0" 
    ads_api_version: str = "v21.0"
    
    # Connection Settings
    api_timeout: int = 30
    retry_count: int = 3
    rate_limit_window: int = 60
    
    # OAuth Settings
    redirect_uri: str = "http://localhost:3000/meta/callback"
    
    # Environment
    environment: MetaEnvironment = MetaEnvironment.DEVELOPMENT
    
    # Feature Flags
    enable_circuit_breaker: bool = True
    enable_health_checks: bool = True
    enable_detailed_logging: bool = False
    
    # Circuit Breaker Settings
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_timeout: float = 300.0
    circuit_breaker_success_threshold: int = 3
    
    # Health Check Settings
    health_check_interval: int = 300
    health_check_timeout: float = 10.0
    
    # Required scopes for different operations
    required_scopes: List[str] = field(default_factory=lambda: [
        'pages_manage_posts',
        'pages_read_engagement', 
        'instagram_basic',
        'instagram_content_publish',
        'ads_management',
        'business_management'
    ])


class MetaConfigManager:
    """
    Centralized configuration manager for Meta API integrations
    Provides validation, caching, and consistent access to Meta configurations
    """
    
    def __init__(self):
        self._config: Optional[MetaAPIConfig] = None
        self._validated: bool = False
        self._validation_errors: List[str] = []
    
    def load_config(self, force_reload: bool = False) -> MetaAPIConfig:
        """
        Load Meta API configuration from environment variables
        
        Args:
            force_reload: Force reload configuration even if cached
            
        Returns:
            MetaAPIConfig instance with loaded configuration
        """
        if self._config is not None and not force_reload:
            return self._config
        
        logger.info("Loading Meta API configuration...")
        
        try:
            # Load core authentication
            access_token = get_config("META_ACCESS_TOKEN")
            app_id = get_config("FACEBOOK_APP_ID")
            app_secret = get_config("FACEBOOK_APP_SECRET")
            
            # Load account IDs
            facebook_page_id = get_config("FACEBOOK_PAGE_ID")
            instagram_business_id = get_config("INSTAGRAM_BUSINESS_ID")
            ad_account_id = get_config("META_AD_ACCOUNT_ID")
            
            # Load API configuration with defaults
            api_version = get_config("META_API_VERSION") or "v21.0"
            graph_api_version = get_config("META_GRAPH_API_VERSION") or api_version
            ads_api_version = get_config("META_ADS_API_VERSION") or api_version
            
            # Load connection settings
            api_timeout = int(get_config("META_API_TIMEOUT") or "30")
            retry_count = int(get_config("META_API_RETRY_COUNT") or "3")
            rate_limit_window = int(get_config("META_RATE_LIMIT_WINDOW") or "60")
            
            # Load OAuth settings
            redirect_uri = get_config("FACEBOOK_REDIRECT_URI") or "http://localhost:3000/meta/callback"
            
            # Load environment
            env_str = get_config("META_ENVIRONMENT") or "development"
            try:
                environment = MetaEnvironment(env_str.lower())
            except ValueError:
                environment = MetaEnvironment.DEVELOPMENT
                logger.warning(f"Invalid META_ENVIRONMENT '{env_str}', using development")
            
            # Load feature flags
            enable_circuit_breaker = get_config("META_ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
            enable_health_checks = get_config("META_ENABLE_HEALTH_CHECKS", "true").lower() == "true"
            enable_detailed_logging = get_config("META_ENABLE_DETAILED_LOGGING", "false").lower() == "true"
            
            # Load circuit breaker settings
            cb_failure_threshold = int(get_config("META_CIRCUIT_BREAKER_FAILURE_THRESHOLD") or "3")
            cb_timeout = float(get_config("META_CIRCUIT_BREAKER_TIMEOUT") or "300.0")
            cb_success_threshold = int(get_config("META_CIRCUIT_BREAKER_SUCCESS_THRESHOLD") or "3")
            
            # Load health check settings
            hc_interval = int(get_config("META_HEALTH_CHECK_INTERVAL") or "300")
            hc_timeout = float(get_config("META_HEALTH_CHECK_TIMEOUT") or "10.0")
            
            # Create configuration instance
            self._config = MetaAPIConfig(
                access_token=access_token,
                app_id=app_id,
                app_secret=app_secret,
                facebook_page_id=facebook_page_id,
                instagram_business_id=instagram_business_id,
                ad_account_id=ad_account_id,
                api_version=api_version,
                graph_api_version=graph_api_version,
                ads_api_version=ads_api_version,
                api_timeout=api_timeout,
                retry_count=retry_count,
                rate_limit_window=rate_limit_window,
                redirect_uri=redirect_uri,
                environment=environment,
                enable_circuit_breaker=enable_circuit_breaker,
                enable_health_checks=enable_health_checks,
                enable_detailed_logging=enable_detailed_logging,
                circuit_breaker_failure_threshold=cb_failure_threshold,
                circuit_breaker_timeout=cb_timeout,
                circuit_breaker_success_threshold=cb_success_threshold,
                health_check_interval=hc_interval,
                health_check_timeout=hc_timeout
            )
            
            logger.info(f"Meta API configuration loaded successfully (environment: {environment.value})")
            return self._config
            
        except ConfigurationError as e:
            logger.error(f"Configuration error loading Meta API settings: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading Meta API configuration: {e}")
            raise ConfigurationError(f"Failed to load Meta API configuration: {e}")
    
    def validate_config(self, config: MetaAPIConfig = None) -> tuple[bool, List[str]]:
        """
        Validate Meta API configuration
        
        Args:
            config: Configuration to validate (uses loaded config if None)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if config is None:
            config = self.get_config()
        
        errors = []
        
        # Validate required authentication
        if not config.access_token:
            errors.append("META_ACCESS_TOKEN is required")
        
        # Validate OAuth configuration for production
        if config.environment == MetaEnvironment.PRODUCTION:
            if not config.app_id:
                errors.append("FACEBOOK_APP_ID is required for production")
            if not config.app_secret:
                errors.append("FACEBOOK_APP_SECRET is required for production")
        
        # Validate API version format
        if not config.api_version.startswith('v') or len(config.api_version) < 3:
            errors.append(f"Invalid API version format: {config.api_version}")
        
        # Validate numeric settings
        if config.api_timeout < 5 or config.api_timeout > 300:
            errors.append("META_API_TIMEOUT must be between 5 and 300 seconds")
        
        if config.retry_count < 1 or config.retry_count > 10:
            errors.append("META_API_RETRY_COUNT must be between 1 and 10")
        
        if config.rate_limit_window < 30 or config.rate_limit_window > 3600:
            errors.append("META_RATE_LIMIT_WINDOW must be between 30 and 3600 seconds")
        
        # Validate circuit breaker settings
        if config.enable_circuit_breaker:
            if config.circuit_breaker_failure_threshold < 1:
                errors.append("Circuit breaker failure threshold must be at least 1")
            
            if config.circuit_breaker_timeout < 10:
                errors.append("Circuit breaker timeout must be at least 10 seconds")
        
        # Validate health check settings
        if config.enable_health_checks:
            if config.health_check_interval < 60:
                errors.append("Health check interval must be at least 60 seconds")
            
            if config.health_check_timeout < 1:
                errors.append("Health check timeout must be at least 1 second")
        
        # Store validation results
        self._validated = len(errors) == 0
        self._validation_errors = errors
        
        if errors:
            logger.error(f"Meta API configuration validation failed: {'; '.join(errors)}")
        else:
            logger.info("Meta API configuration validation passed")
        
        return self._validated, errors
    
    def get_config(self) -> MetaAPIConfig:
        """Get current Meta API configuration"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def is_validated(self) -> bool:
        """Check if configuration has been validated"""
        return self._validated
    
    def get_validation_errors(self) -> List[str]:
        """Get configuration validation errors"""
        return self._validation_errors.copy()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary (without sensitive data)"""
        config = self.get_config()
        
        return {
            'api_version': config.api_version,
            'environment': config.environment.value,
            'has_access_token': bool(config.access_token),
            'has_app_credentials': bool(config.app_id and config.app_secret),
            'has_facebook_page': bool(config.facebook_page_id),
            'has_instagram_account': bool(config.instagram_business_id),
            'has_ad_account': bool(config.ad_account_id),
            'api_timeout': config.api_timeout,
            'retry_count': config.retry_count,
            'circuit_breaker_enabled': config.enable_circuit_breaker,
            'health_checks_enabled': config.enable_health_checks,
            'validation_status': 'passed' if self._validated else 'failed',
            'validation_errors': self._validation_errors
        }
    
    def get_graph_api_url(self, endpoint: str = "") -> str:
        """Get Graph API URL for given endpoint"""
        config = self.get_config()
        base_url = f"https://graph.facebook.com/{config.graph_api_version}"
        return f"{base_url}/{endpoint}" if endpoint else base_url
    
    def get_ads_api_url(self, endpoint: str = "") -> str:
        """Get Ads API URL for given endpoint"""
        config = self.get_config()
        base_url = f"https://graph.facebook.com/{config.ads_api_version}"
        return f"{base_url}/{endpoint}" if endpoint else base_url


# Global configuration manager instance
meta_config = MetaConfigManager()


def get_meta_config() -> MetaAPIConfig:
    """Get Meta API configuration (convenience function)"""
    return meta_config.get_config()


def validate_meta_config() -> tuple[bool, List[str]]:
    """Validate Meta API configuration (convenience function)"""
    return meta_config.validate_config()


def get_meta_config_summary() -> Dict[str, Any]:
    """Get Meta API configuration summary (convenience function)"""
    return meta_config.get_config_summary()