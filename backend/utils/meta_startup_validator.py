"""
Meta API startup validation service
Validates all Meta configurations and dependencies on application startup
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp

from .meta_config import get_meta_config, validate_meta_config, MetaEnvironment
from .meta_health_check import get_meta_health_status

logger = logging.getLogger(__name__)


class MetaStartupValidationError(Exception):
    """Exception raised when Meta startup validation fails"""
    pass


class MetaStartupValidator:
    """
    Comprehensive startup validator for Meta API integrations
    Validates configuration, connectivity, permissions, and dependencies
    """
    
    def __init__(self):
        self.validation_results: Dict[str, Any] = {}
        self.startup_time = datetime.now()
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate Meta API configuration"""
        logger.info("Validating Meta API configuration...")
        
        try:
            config = get_meta_config()
            is_valid, errors = validate_meta_config()
            
            result = {
                'status': 'passed' if is_valid else 'failed',
                'errors': errors,
                'config_summary': {
                    'api_version': config.api_version,
                    'environment': config.environment.value,
                    'has_access_token': bool(config.access_token),
                    'has_app_credentials': bool(config.app_id and config.app_secret),
                    'has_facebook_page': bool(config.facebook_page_id),
                    'has_instagram_account': bool(config.instagram_business_id),
                    'has_ad_account': bool(config.ad_account_id),
                    'circuit_breaker_enabled': config.enable_circuit_breaker,
                    'health_checks_enabled': config.enable_health_checks
                }
            }
            
            if is_valid:
                logger.info("✅ Meta API configuration validation passed")
            else:
                logger.error(f"❌ Meta API configuration validation failed: {'; '.join(errors)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Meta API configuration validation error: {e}")
            return {
                'status': 'error',
                'errors': [str(e)],
                'config_summary': {}
            }
    
    async def validate_api_connectivity(self) -> Dict[str, Any]:
        """Validate Meta API connectivity"""
        logger.info("Validating Meta API connectivity...")
        
        try:
            health_status = await get_meta_health_status()
            
            result = {
                'status': health_status['overall_status'].lower(),
                'services': health_status.get('services', {}),
                'response_time': health_status.get('average_response_time_ms'),
                'healthy_services': health_status.get('healthy_services', 0),
                'total_services': health_status.get('services_checked', 0)
            }
            
            if health_status['overall_status'] == 'HEALTHY':
                logger.info("✅ Meta API connectivity validation passed")
            else:
                logger.warning(f"⚠️ Meta API connectivity issues detected: {health_status['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Meta API connectivity validation error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'services': {}
            }
    
    async def validate_permissions_and_scopes(self) -> Dict[str, Any]:
        """Validate Meta API permissions and scopes"""
        logger.info("Validating Meta API permissions and scopes...")
        
        try:
            config = get_meta_config()
            
            if not config.access_token:
                return {
                    'status': 'skipped',
                    'message': 'No access token available for permission validation'
                }
            
            # Check token permissions via Graph API
            permissions_url = f"https://graph.facebook.com/{config.graph_api_version}/me/permissions"
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    permissions_url,
                    params={'access_token': config.access_token}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        granted_permissions = [
                            perm['permission'] for perm in data.get('data', [])
                            if perm.get('status') == 'granted'
                        ]
                        
                        # Check for required scopes
                        missing_scopes = []
                        for required_scope in config.required_scopes:
                            if required_scope not in granted_permissions:
                                missing_scopes.append(required_scope)
                        
                        result = {
                            'status': 'passed' if not missing_scopes else 'warning',
                            'granted_permissions': granted_permissions,
                            'required_scopes': config.required_scopes,
                            'missing_scopes': missing_scopes,
                            'permission_count': len(granted_permissions)
                        }
                        
                        if not missing_scopes:
                            logger.info("✅ Meta API permissions validation passed")
                        else:
                            logger.warning(f"⚠️ Missing Meta API scopes: {', '.join(missing_scopes)}")
                        
                        return result
                    else:
                        error_text = await response.text()
                        return {
                            'status': 'failed',
                            'error': f"Permission check failed: {response.status} - {error_text}"
                        }
        
        except Exception as e:
            logger.error(f"❌ Meta API permissions validation error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def validate_account_access(self) -> Dict[str, Any]:
        """Validate access to Meta accounts and pages"""
        logger.info("Validating Meta account access...")
        
        try:
            config = get_meta_config()
            
            if not config.access_token:
                return {
                    'status': 'skipped',
                    'message': 'No access token available for account validation'
                }
            
            results = {
                'facebook_page': {'status': 'not_configured'},
                'instagram_account': {'status': 'not_configured'},
                'ad_account': {'status': 'not_configured'}
            }
            
            # Check Facebook Page access
            if config.facebook_page_id:
                try:
                    page_url = f"https://graph.facebook.com/{config.graph_api_version}/{config.facebook_page_id}"
                    timeout = aiohttp.ClientTimeout(total=10.0)
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(
                            page_url,
                            params={'access_token': config.access_token, 'fields': 'id,name,access_token'}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                results['facebook_page'] = {
                                    'status': 'accessible',
                                    'name': data.get('name'),
                                    'id': data.get('id'),
                                    'has_page_token': bool(data.get('access_token'))
                                }
                            else:
                                results['facebook_page'] = {
                                    'status': 'inaccessible',
                                    'error': f"HTTP {response.status}"
                                }
                except Exception as e:
                    results['facebook_page'] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Check Instagram Business Account access
            if config.instagram_business_id:
                try:
                    ig_url = f"https://graph.facebook.com/{config.graph_api_version}/{config.instagram_business_id}"
                    timeout = aiohttp.ClientTimeout(total=10.0)
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(
                            ig_url,
                            params={'access_token': config.access_token, 'fields': 'id,username'}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                results['instagram_account'] = {
                                    'status': 'accessible',
                                    'username': data.get('username'),
                                    'id': data.get('id')
                                }
                            else:
                                results['instagram_account'] = {
                                    'status': 'inaccessible',
                                    'error': f"HTTP {response.status}"
                                }
                except Exception as e:
                    results['instagram_account'] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Check Ad Account access
            if config.ad_account_id:
                try:
                    ad_account_url = f"https://graph.facebook.com/{config.ads_api_version}/act_{config.ad_account_id}"
                    timeout = aiohttp.ClientTimeout(total=10.0)
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(
                            ad_account_url,
                            params={'access_token': config.access_token, 'fields': 'id,name,account_status'}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                results['ad_account'] = {
                                    'status': 'accessible',
                                    'name': data.get('name'),
                                    'id': data.get('id'),
                                    'account_status': data.get('account_status')
                                }
                            else:
                                results['ad_account'] = {
                                    'status': 'inaccessible',
                                    'error': f"HTTP {response.status}"
                                }
                except Exception as e:
                    results['ad_account'] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Determine overall status
            accessible_count = sum(1 for result in results.values() if result['status'] == 'accessible')
            total_configured = sum(1 for result in results.values() if result['status'] != 'not_configured')
            
            if total_configured == 0:
                overall_status = 'not_configured'
            elif accessible_count == total_configured:
                overall_status = 'passed'
            elif accessible_count > 0:
                overall_status = 'partial'
            else:
                overall_status = 'failed'
            
            result = {
                'status': overall_status,
                'accounts': results,
                'accessible_count': accessible_count,
                'total_configured': total_configured
            }
            
            if overall_status == 'passed':
                logger.info("✅ Meta account access validation passed")
            elif overall_status == 'partial':
                logger.warning("⚠️ Meta account access partially successful")
            elif overall_status == 'not_configured':
                logger.info("ℹ️ Meta accounts not configured")
            else:
                logger.error("❌ Meta account access validation failed")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Meta account access validation error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_startup_validation(self, strict_mode: bool = False) -> Dict[str, Any]:
        """
        Run complete startup validation
        
        Args:
            strict_mode: If True, raise exception on any validation failure
            
        Returns:
            Complete validation results
        """
        logger.info("🚀 Starting Meta API startup validation...")
        
        # Run all validations concurrently
        validation_tasks = [
            self.validate_configuration(),
            self.validate_api_connectivity(),
            self.validate_permissions_and_scopes(),
            self.validate_account_access()
        ]
        
        try:
            results = await asyncio.gather(*validation_tasks)
            
            self.validation_results = {
                'timestamp': self.startup_time.isoformat(),
                'configuration': results[0],
                'connectivity': results[1],
                'permissions': results[2],
                'accounts': results[3],
            }
            
            # Determine overall status
            critical_failures = []
            warnings = []
            
            if self.validation_results['configuration']['status'] == 'failed':
                critical_failures.extend(self.validation_results['configuration']['errors'])
            
            if self.validation_results['connectivity']['status'] == 'error':
                critical_failures.append("API connectivity check failed")
            elif self.validation_results['connectivity']['status'] == 'unhealthy':
                warnings.append("Some API services are unhealthy")
            
            if self.validation_results['permissions']['status'] == 'failed':
                warnings.append("Permission validation failed")
            
            if self.validation_results['accounts']['status'] == 'failed':
                warnings.append("Account access validation failed")
            
            # Set overall status
            if critical_failures:
                overall_status = 'FAILED'
                message = f"Critical validation failures: {'; '.join(critical_failures)}"
            elif warnings:
                overall_status = 'WARNING'
                message = f"Validation warnings: {'; '.join(warnings)}"
            else:
                overall_status = 'PASSED'
                message = "All Meta API startup validations passed successfully"
            
            self.validation_results['overall_status'] = overall_status
            self.validation_results['message'] = message
            self.validation_results['critical_failures'] = critical_failures
            self.validation_results['warnings'] = warnings
            
            # Log results
            if overall_status == 'PASSED':
                logger.info(f"✅ {message}")
            elif overall_status == 'WARNING':
                logger.warning(f"⚠️ {message}")
            else:
                logger.error(f"❌ {message}")
            
            # Raise exception in strict mode for critical failures
            if strict_mode and critical_failures:
                raise MetaStartupValidationError(message)
            
            return self.validation_results
            
        except Exception as e:
            logger.error(f"❌ Meta API startup validation failed: {e}")
            if strict_mode:
                raise MetaStartupValidationError(f"Startup validation failed: {e}")
            
            return {
                'timestamp': self.startup_time.isoformat(),
                'overall_status': 'ERROR',
                'message': f"Startup validation failed: {str(e)}",
                'error': str(e)
            }
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation results summary"""
        if not self.validation_results:
            return {'status': 'not_run', 'message': 'Validation not yet performed'}
        
        return {
            'status': self.validation_results['overall_status'],
            'message': self.validation_results['message'],
            'timestamp': self.validation_results['timestamp'],
            'summary': {
                'configuration': self.validation_results['configuration']['status'],
                'connectivity': self.validation_results['connectivity']['status'],
                'permissions': self.validation_results['permissions']['status'],
                'accounts': self.validation_results['accounts']['status']
            }
        }


# Global startup validator instance
startup_validator = MetaStartupValidator()


async def validate_meta_startup(strict_mode: bool = False) -> Dict[str, Any]:
    """Run Meta API startup validation (convenience function)"""
    return await startup_validator.run_startup_validation(strict_mode=strict_mode)


def get_startup_validation_summary() -> Dict[str, Any]:
    """Get startup validation summary (convenience function)"""
    return startup_validator.get_validation_summary()