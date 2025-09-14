"""
Circuit Breaker Pattern implementation for Meta APIs
Prevents cascading failures and provides fallback strategies
"""
import asyncio
import time
import logging
from enum import Enum
from typing import Dict, Any, Callable, Optional, Union
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Blocking all requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Number of failures to open circuit
    timeout: float = 60.0              # Time to wait before trying again (seconds)
    expected_exception: Exception = Exception  # Exception type that triggers circuit
    success_threshold: int = 3          # Successful calls needed to close circuit in HALF_OPEN


class MetaAPICircuitBreaker:
    """
    Circuit breaker for Meta API calls
    Prevents cascading failures and provides fallback mechanisms
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")
    
    def can_execute(self) -> bool:
        """Check if the circuit allows execution"""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self.last_failure_time and (
                    time.time() - self.last_failure_time >= self.config.timeout
                ):
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
                    return True
                return False
            
            # HALF_OPEN state - allow limited requests
            return True
    
    def record_success(self):
        """Record a successful call"""
        with self.lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
                    logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")
    
    def record_failure(self, exception: Exception):
        """Record a failed call"""
        with self.lock:
            if isinstance(exception, type(self.config.expected_exception)):
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.state == CircuitState.HALF_OPEN:
                    # Failed during recovery - go back to OPEN
                    self.state = CircuitState.OPEN
                    self.success_count = 0
                    logger.warning(f"Circuit breaker '{self.name}' failed during recovery - reopened")
                
                elif (self.state == CircuitState.CLOSED and 
                      self.failure_count >= self.config.failure_threshold):
                    # Too many failures - open circuit
                    self.state = CircuitState.OPEN
                    logger.error(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'timeout': self.config.timeout,
                    'success_threshold': self.config.success_threshold
                }
            }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    def __init__(self, circuit_name: str, retry_after: float = None):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        message = f"Circuit breaker '{circuit_name}' is open"
        if retry_after:
            message += f" - retry after {retry_after:.1f} seconds"
        super().__init__(message)


class MetaAPICircuitBreakerManager:
    """
    Manager for multiple Meta API circuit breakers
    Provides centralized monitoring and fallback strategies
    """
    
    def __init__(self):
        self.breakers: Dict[str, MetaAPICircuitBreaker] = {}
        self.lock = Lock()
    
    def get_breaker(self, name: str, config: CircuitBreakerConfig = None) -> MetaAPICircuitBreaker:
        """Get or create a circuit breaker"""
        with self.lock:
            if name not in self.breakers:
                self.breakers[name] = MetaAPICircuitBreaker(name, config)
            return self.breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state information for all circuit breakers"""
        with self.lock:
            return {name: breaker.get_state_info() 
                    for name, breaker in self.breakers.items()}
    
    def reset_breaker(self, name: str) -> bool:
        """Manually reset a circuit breaker"""
        with self.lock:
            if name in self.breakers:
                breaker = self.breakers[name]
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                breaker.last_failure_time = None
                logger.info(f"Circuit breaker '{name}' manually reset")
                return True
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of all circuits"""
        states = self.get_all_states()
        
        total = len(states)
        closed = sum(1 for state in states.values() if state['state'] == 'CLOSED')
        open_circuits = [name for name, state in states.items() if state['state'] == 'OPEN']
        half_open = sum(1 for state in states.values() if state['state'] == 'HALF_OPEN')
        
        return {
            'total_circuits': total,
            'healthy_circuits': closed,
            'open_circuits': len(open_circuits),
            'recovering_circuits': half_open,
            'health_percentage': (closed / total * 100) if total > 0 else 100,
            'open_circuit_names': open_circuits,
            'overall_status': 'HEALTHY' if closed == total else 'DEGRADED' if open_circuits else 'RECOVERING'
        }


# Global circuit breaker manager instance
circuit_manager = MetaAPICircuitBreakerManager()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: Exception = Exception,
    success_threshold: int = 3,
    fallback: Optional[Callable] = None
):
    """
    Decorator for implementing circuit breaker pattern on Meta API functions
    
    Args:
        name: Unique name for the circuit breaker
        failure_threshold: Number of failures to open circuit
        timeout: Time to wait before trying again (seconds)
        expected_exception: Exception type that triggers circuit
        success_threshold: Successful calls needed to close circuit
        fallback: Optional fallback function to call when circuit is open
    """
    def decorator(func):
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
            success_threshold=success_threshold
        )
        breaker = circuit_manager.get_breaker(name, config)
        
        async def async_wrapper(*args, **kwargs):
            # Check if circuit allows execution
            if not breaker.can_execute():
                retry_after = None
                if breaker.last_failure_time:
                    retry_after = breaker.config.timeout - (time.time() - breaker.last_failure_time)
                
                if fallback:
                    logger.warning(f"Circuit breaker '{name}' is open, using fallback")
                    if asyncio.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    else:
                        return fallback(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenError(name, retry_after)
            
            # Execute the function
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure(e)
                raise e
        
        def sync_wrapper(*args, **kwargs):
            # Check if circuit allows execution
            if not breaker.can_execute():
                retry_after = None
                if breaker.last_failure_time:
                    retry_after = breaker.config.timeout - (time.time() - breaker.last_failure_time)
                
                if fallback:
                    logger.warning(f"Circuit breaker '{name}' is open, using fallback")
                    return fallback(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenError(name, retry_after)
            
            # Execute the function
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure(e)
                raise e
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator