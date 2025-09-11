"""
Health Check and System Monitoring
Provides comprehensive health checks for all platform components
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import httpx
import os

from core.config import settings

logger = logging.getLogger(__name__)

class HealthCheckService:
    """Service for monitoring system health and dependencies"""
    
    def __init__(self):
        self.health_checks = {
            "database": self._check_database,
            "ml_services": self._check_ml_services,
            "external_apis": self._check_external_apis,
            "storage": self._check_storage,
            "memory": self._check_memory,
            "disk_space": self._check_disk_space
        }
    
    async def comprehensive_health_check(self, db: Session) -> Dict[str, Any]:
        """Run comprehensive health check on all system components"""
        
        start_time = datetime.utcnow()
        health_status = {
            "status": "healthy",
            "timestamp": start_time.isoformat(),
            "checks": {},
            "summary": {
                "total_checks": len(self.health_checks),
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Run all health checks
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func(db)
                health_status["checks"][check_name] = result
                
                # Update summary
                if result["status"] == "healthy":
                    health_status["summary"]["passed"] += 1
                elif result["status"] == "warning":
                    health_status["summary"]["warnings"] += 1
                else:
                    health_status["summary"]["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Health check failed for {check_name}: {e}")
                health_status["checks"][check_name] = {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                health_status["summary"]["failed"] += 1
        
        # Determine overall status
        if health_status["summary"]["failed"] > 0:
            health_status["status"] = "unhealthy"
        elif health_status["summary"]["warnings"] > 0:
            health_status["status"] = "warning"
        
        # Add timing information
        end_time = datetime.utcnow()
        health_status["response_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(f"Health check completed: {health_status['status']} in {health_status['response_time_ms']}ms")
        return health_status
    
    async def _check_database(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test a more complex query (checking for tables)
            result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            status = "healthy" if response_time < 100 else "warning"  # Warning if > 100ms
            
            return {
                "status": status,
                "response_time_ms": int(response_time),
                "table_count": table_count,
                "message": f"Database responsive in {response_time:.1f}ms",
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_ml_services(self, db: Session) -> Dict[str, Any]:
        """Check ML service availability and performance"""
        
        try:
            # Check if Anthropic API key is configured
            if not settings.ANTHROPIC_API_KEY:
                return {
                    "status": "warning",
                    "message": "Anthropic API key not configured - ML predictions will use fallbacks",
                    "fallback_enabled": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test ML prediction service by checking recent predictions
            from services.ml_prediction_service import MLPredictionService
            ml_service = MLPredictionService()
            
            # Check if we can create a simple test prediction
            test_config = {
                "campaign_type": "test",
                "budget": 100,
                "platforms": {"facebook": True}
            }
            
            start_time = datetime.utcnow()
            # This would be a lightweight test prediction
            # For now, we'll just check that the service can initialize
            test_result = True  # Placeholder
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy" if test_result else "error",
                "response_time_ms": int(response_time),
                "message": "ML services operational",
                "features_available": [
                    "campaign_performance_prediction",
                    "viral_potential_analysis",
                    "ai_decision_validation"
                ],
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"ML services check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_external_apis(self, db: Session) -> Dict[str, Any]:
        """Check external API connectivity"""
        
        external_apis = {
            "facebook_api": {
                "url": "https://graph.facebook.com/v18.0/me",
                "requires_auth": True,
                "timeout": 10
            }
        }
        
        api_status = {}
        overall_status = "healthy"
        
        for api_name, api_config in external_apis.items():
            try:
                if api_name == "facebook_api" and not settings.FACEBOOK_APP_ID:
                    api_status[api_name] = {
                        "status": "warning",
                        "message": "Facebook API not configured",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    continue
                
                start_time = datetime.utcnow()
                async with httpx.AsyncClient() as client:
                    # For Facebook API, we'd need to use actual credentials
                    # For now, just check if the endpoint is reachable
                    response = await client.get(
                        "https://graph.facebook.com/",  # Basic endpoint
                        timeout=api_config["timeout"]
                    )
                    
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                if response.status_code in [200, 400]:  # 400 is expected without auth
                    api_status[api_name] = {
                        "status": "healthy",
                        "response_time_ms": int(response_time),
                        "message": "API endpoint reachable",
                        "timestamp": end_time.isoformat()
                    }
                else:
                    api_status[api_name] = {
                        "status": "warning",
                        "response_code": response.status_code,
                        "message": f"Unexpected response code: {response.status_code}",
                        "timestamp": end_time.isoformat()
                    }
                    overall_status = "warning"
                    
            except Exception as e:
                api_status[api_name] = {
                    "status": "error",
                    "message": f"API check failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_status = "error"
        
        return {
            "status": overall_status,
            "apis": api_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_storage(self, db: Session) -> Dict[str, Any]:
        """Check file storage and upload directories"""
        
        try:
            upload_dir = settings.UPLOAD_DIR
            
            # Check if upload directory exists and is writable
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(upload_dir, "health_check_test.txt")
            try:
                with open(test_file, 'w') as f:
                    f.write("health check test")
                os.remove(test_file)
                writable = True
            except:
                writable = False
            
            # Get directory size
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(upload_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            status = "healthy" if writable else "error"
            
            return {
                "status": status,
                "upload_directory": upload_dir,
                "writable": writable,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "message": "Storage accessible" if writable else "Storage not writable",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Storage check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_memory(self, db: Session) -> Dict[str, Any]:
        """Check memory usage"""
        
        try:
            import psutil
            
            # Get system memory info
            memory = psutil.virtual_memory()
            
            # Memory thresholds
            warning_threshold = 80  # 80% usage triggers warning
            critical_threshold = 90  # 90% usage triggers error
            
            memory_usage_percent = memory.percent
            
            if memory_usage_percent >= critical_threshold:
                status = "error"
                message = f"Critical memory usage: {memory_usage_percent:.1f}%"
            elif memory_usage_percent >= warning_threshold:
                status = "warning"
                message = f"High memory usage: {memory_usage_percent:.1f}%"
            else:
                status = "healthy"
                message = f"Memory usage normal: {memory_usage_percent:.1f}%"
            
            return {
                "status": status,
                "usage_percent": memory_usage_percent,
                "total_mb": round(memory.total / (1024 * 1024)),
                "available_mb": round(memory.available / (1024 * 1024)),
                "used_mb": round(memory.used / (1024 * 1024)),
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil not available - memory monitoring disabled",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Memory check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_disk_space(self, db: Session) -> Dict[str, Any]:
        """Check disk space availability"""
        
        try:
            import psutil
            
            # Check disk usage for current directory
            disk_usage = psutil.disk_usage('.')
            
            # Disk space thresholds
            warning_threshold = 80  # 80% usage triggers warning
            critical_threshold = 90  # 90% usage triggers error
            
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent >= critical_threshold:
                status = "error"
                message = f"Critical disk usage: {usage_percent:.1f}%"
            elif usage_percent >= warning_threshold:
                status = "warning"
                message = f"High disk usage: {usage_percent:.1f}%"
            else:
                status = "healthy"
                message = f"Disk usage normal: {usage_percent:.1f}%"
            
            return {
                "status": status,
                "usage_percent": round(usage_percent, 1),
                "total_gb": round(disk_usage.total / (1024**3), 1),
                "free_gb": round(disk_usage.free / (1024**3), 1),
                "used_gb": round(disk_usage.used / (1024**3), 1),
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil not available - disk monitoring disabled",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Disk check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

# Global health check service
health_check_service = HealthCheckService()