"""
Health check service for Meta API integrations
Monitors Facebook Agent, Meta Ads Automation, and circuit breaker states
"""
import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .circuit_breaker import circuit_manager
from .config_manager import get_config

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class ServiceHealth:
    """Health information for a service"""
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MetaHealthChecker:
    """Health checker for Meta API services"""
    
    def __init__(self):
        self.last_checks: Dict[str, ServiceHealth] = {}
        self.check_interval = 300  # 5 minutes
    
    async def check_facebook_api_health(self) -> ServiceHealth:
        """Check Facebook Graph API health"""
        service_name = "facebook_graph_api"
        start_time = time.time()
        
        try:
            access_token = get_config("META_ACCESS_TOKEN")
            if not access_token:
                return ServiceHealth(
                    name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    error_message="META_ACCESS_TOKEN not configured"
                )
            
            # Test basic Graph API connectivity
            api_version = get_config("META_API_VERSION") or "v21.0"
            test_url = f"https://graph.facebook.com/{api_version}/me"
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    test_url,
                    params={'access_token': access_token, 'fields': 'id,name'}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            metadata={'user_id': data.get('id'), 'api_version': api_version}
                        )
                    elif response.status == 401:
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            error_message="Invalid or expired access token"
                        )
                    else:
                        error_text = await response.text()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.DEGRADED,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            error_message=f"API returned {response.status}: {error_text}"
                        )
                        
        except asyncio.TimeoutError:
            return ServiceHealth(
                name=service_name,
                status=HealthStatus.DEGRADED,
                last_check=datetime.now(),
                error_message="Request timeout"
            )
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_instagram_api_health(self) -> ServiceHealth:
        """Check Instagram Business API health"""
        service_name = "instagram_business_api"
        start_time = time.time()
        
        try:
            access_token = get_config("META_ACCESS_TOKEN")
            instagram_business_id = get_config("INSTAGRAM_BUSINESS_ID")
            
            if not access_token:
                return ServiceHealth(
                    name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    error_message="META_ACCESS_TOKEN not configured"
                )
            
            if not instagram_business_id:
                return ServiceHealth(
                    name=service_name,
                    status=HealthStatus.DEGRADED,
                    error_message="INSTAGRAM_BUSINESS_ID not configured"
                )
            
            # Test Instagram Business API connectivity
            api_version = get_config("META_API_VERSION") or "v21.0"
            test_url = f"https://graph.facebook.com/{api_version}/{instagram_business_id}"
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    test_url,
                    params={'access_token': access_token, 'fields': 'id,username'}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            metadata={'account_id': data.get('id'), 'username': data.get('username')}
                        )
                    else:
                        error_text = await response.text()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.DEGRADED,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            error_message=f"API returned {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_meta_ads_api_health(self) -> ServiceHealth:
        """Check Meta Ads API health"""
        service_name = "meta_ads_api"
        start_time = time.time()
        
        try:
            access_token = get_config("META_ACCESS_TOKEN")
            if not access_token:
                return ServiceHealth(
                    name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    error_message="META_ACCESS_TOKEN not configured"
                )
            
            # Test Meta Marketing API connectivity
            api_version = get_config("META_API_VERSION") or "v21.0"
            test_url = f"https://graph.facebook.com/{api_version}/me/adaccounts"
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    test_url,
                    params={'access_token': access_token, 'fields': 'id,name', 'limit': 1}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            metadata={'ad_accounts_available': len(data.get('data', []))}
                        )
                    else:
                        error_text = await response.text()
                        return ServiceHealth(
                            name=service_name,
                            status=HealthStatus.DEGRADED,
                            response_time_ms=response_time,
                            last_check=datetime.now(),
                            error_message=f"API returned {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    def check_circuit_breaker_health(self) -> ServiceHealth:
        """Check circuit breaker health"""
        service_name = "circuit_breakers"
        
        try:
            health_status = circuit_manager.get_health_status()
            
            if health_status['overall_status'] == 'HEALTHY':
                status = HealthStatus.HEALTHY
            elif health_status['overall_status'] == 'DEGRADED':
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            error_message = None
            if health_status['open_circuits'] > 0:
                error_message = f"Open circuits: {', '.join(health_status['open_circuit_names'])}"
            
            return ServiceHealth(
                name=service_name,
                status=status,
                last_check=datetime.now(),
                error_message=error_message,
                metadata=health_status
            )
            
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def run_all_health_checks(self) -> Dict[str, ServiceHealth]:
        """Run all health checks concurrently"""
        logger.info("Running Meta API health checks...")
        
        # Run all checks concurrently
        tasks = [
            self.check_facebook_api_health(),
            self.check_instagram_api_health(),
            self.check_meta_ads_api_health(),
        ]
        
        # Run async checks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Run sync check
        circuit_health = self.check_circuit_breaker_health()
        
        # Process results
        health_status = {}
        service_names = ["facebook_graph_api", "instagram_business_api", "meta_ads_api"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                health_status[service_names[i]] = ServiceHealth(
                    name=service_names[i],
                    status=HealthStatus.UNKNOWN,
                    last_check=datetime.now(),
                    error_message=str(result)
                )
            else:
                health_status[service_names[i]] = result
        
        health_status["circuit_breakers"] = circuit_health
        
        # Update last checks
        self.last_checks.update(health_status)
        
        return health_status
    
    def get_overall_health(self, health_checks: Dict[str, ServiceHealth] = None) -> Dict[str, Any]:
        """Get overall system health summary"""
        if health_checks is None:
            health_checks = self.last_checks
        
        if not health_checks:
            return {
                'overall_status': HealthStatus.UNKNOWN.value,
                'message': 'No health checks performed yet',
                'timestamp': datetime.now().isoformat()
            }
        
        # Analyze health status
        statuses = [health.status for health in health_checks.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
            message = "All Meta API services are healthy"
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            unhealthy_services = [
                name for name, health in health_checks.items() 
                if health.status == HealthStatus.UNHEALTHY
            ]
            overall_status = HealthStatus.UNHEALTHY
            message = f"Unhealthy services: {', '.join(unhealthy_services)}"
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            degraded_services = [
                name for name, health in health_checks.items() 
                if health.status == HealthStatus.DEGRADED
            ]
            overall_status = HealthStatus.DEGRADED
            message = f"Degraded services: {', '.join(degraded_services)}"
        else:
            overall_status = HealthStatus.UNKNOWN
            message = "Unable to determine overall health"
        
        # Calculate average response time
        response_times = [
            health.response_time_ms for health in health_checks.values()
            if health.response_time_ms is not None
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        return {
            'overall_status': overall_status.value,
            'message': message,
            'services_checked': len(health_checks),
            'healthy_services': len([h for h in health_checks.values() if h.status == HealthStatus.HEALTHY]),
            'degraded_services': len([h for h in health_checks.values() if h.status == HealthStatus.DEGRADED]),
            'unhealthy_services': len([h for h in health_checks.values() if h.status == HealthStatus.UNHEALTHY]),
            'average_response_time_ms': avg_response_time,
            'timestamp': datetime.now().isoformat(),
            'services': {name: asdict(health) for name, health in health_checks.items()}
        }


# Global health checker instance
health_checker = MetaHealthChecker()


async def get_meta_health_status() -> Dict[str, Any]:
    """Get current Meta API health status"""
    health_checks = await health_checker.run_all_health_checks()
    return health_checker.get_overall_health(health_checks)


def get_cached_meta_health_status() -> Dict[str, Any]:
    """Get cached Meta API health status (doesn't run new checks)"""
    return health_checker.get_overall_health()


async def run_health_check_daemon():
    """Run health check daemon (for background monitoring)"""
    logger.info("Starting Meta API health check daemon")
    
    while True:
        try:
            await health_checker.run_all_health_checks()
            logger.info("Health checks completed successfully")
            await asyncio.sleep(health_checker.check_interval)
        except Exception as e:
            logger.error(f"Health check daemon error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error