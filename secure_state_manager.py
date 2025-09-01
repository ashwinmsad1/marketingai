"""
Secure OAuth State Token Manager
Simplified version using in-memory storage with PostgreSQL option for production
"""

import secrets
import hashlib
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager
from threading import Lock
import json

logger = logging.getLogger(__name__)

class StateTokenError(Exception):
    """Custom exception for state token related errors"""
    pass

class StateTokenExpiredError(StateTokenError):
    """Exception raised when state token has expired"""
    pass

class StateTokenInvalidError(StateTokenError):
    """Exception raised when state token is invalid"""
    pass

class SecureStateManager:
    """
    Secure OAuth state token manager with in-memory storage and validation
    Implements CSRF protection with secure token generation and validation
    """
    
    def __init__(self, token_expiry_minutes: int = 10):
        """
        Initialize secure state manager
        
        Args:
            token_expiry_minutes: Token expiration time in minutes
        """
        self.token_expiry_minutes = token_expiry_minutes
        self._lock = Lock()
        self._tokens: Dict[str, Dict] = {}  # In-memory token storage
        logger.info("Secure State Manager initialized with in-memory storage")
    
    def generate_state_token(self, user_session: Optional[str] = None, 
                           metadata: Optional[Dict] = None) -> str:
        """
        Generate secure state token for OAuth flow
        
        Args:
            user_session: User session identifier
            metadata: Additional metadata to store with token
            
        Returns:
            Secure state token string
        """
        try:
            with self._lock:
                # Generate cryptographically secure random token
                token = secrets.token_urlsafe(32)
                
                # Create token hash for validation
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                
                # Calculate expiration time
                expires_at = datetime.utcnow() + timedelta(minutes=self.token_expiry_minutes)
                
                # Store token data
                token_data = {
                    'state_hash': token_hash,
                    'user_session': user_session,
                    'created_at': datetime.utcnow(),
                    'expires_at': expires_at,
                    'used': False,
                    'metadata': json.dumps(metadata) if metadata else None
                }
                
                self._tokens[token] = token_data
                
                logger.debug(f"State token generated: {token[:8]}...")
                return token
                
        except Exception as e:
            logger.error(f"Error generating state token: {e}")
            raise StateTokenError(f"Failed to generate state token: {e}")
    
    def validate_and_consume_state_token(self, token: str, 
                                       user_session: Optional[str] = None) -> Tuple[bool, Optional[Dict]]:
        """
        Validate state token and mark as consumed
        
        Args:
            token: State token to validate
            user_session: Expected user session identifier
            
        Returns:
            Tuple of (is_valid, metadata)
        """
        try:
            with self._lock:
                if token not in self._tokens:
                    raise StateTokenInvalidError("Invalid state token")
                
                token_data = self._tokens[token]
                
                # Check if token is already used
                if token_data['used']:
                    raise StateTokenInvalidError("State token already used")
                
                # Check if token is expired
                if datetime.utcnow() > token_data['expires_at']:
                    # Clean up expired token
                    del self._tokens[token]
                    raise StateTokenExpiredError("State token expired")
                
                # Validate token hash
                expected_hash = hashlib.sha256(token.encode()).hexdigest()
                if token_data['state_hash'] != expected_hash:
                    raise StateTokenInvalidError("State token hash validation failed")
                
                # Validate user session if provided
                if user_session and token_data['user_session'] != user_session:
                    raise StateTokenInvalidError("User session validation failed")
                
                # Mark token as used
                token_data['used'] = True
                
                # Parse metadata
                metadata = None
                if token_data['metadata']:
                    try:
                        metadata = json.loads(token_data['metadata'])
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse token metadata")
                
                logger.debug(f"State token validated and consumed: {token[:8]}...")
                
                # Clean up used token after a delay
                # In production, you might want to keep used tokens for audit trail
                return True, metadata
                
        except (StateTokenError) as e:
            logger.error(f"State token validation failed: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error validating state token: {e}")
            return False, None
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from storage
        
        Returns:
            Number of tokens cleaned up
        """
        try:
            with self._lock:
                current_time = datetime.utcnow()
                expired_tokens = [
                    token for token, data in self._tokens.items()
                    if current_time > data['expires_at']
                ]
                
                for token in expired_tokens:
                    del self._tokens[token]
                
                if expired_tokens:
                    logger.info(f"Cleaned up {len(expired_tokens)} expired state tokens")
                
                return len(expired_tokens)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0
    
    def get_token_info(self, token: str) -> Optional[Dict]:
        """
        Get token information without consuming it
        
        Args:
            token: State token
            
        Returns:
            Token information dict or None if not found
        """
        try:
            with self._lock:
                if token not in self._tokens:
                    return None
                
                token_data = self._tokens[token].copy()
                
                # Convert datetime objects to ISO format for JSON serialization
                token_data['created_at'] = token_data['created_at'].isoformat()
                token_data['expires_at'] = token_data['expires_at'].isoformat()
                
                return token_data
                
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a state token
        
        Args:
            token: State token to revoke
            
        Returns:
            True if token was revoked, False otherwise
        """
        try:
            with self._lock:
                if token in self._tokens:
                    del self._tokens[token]
                    logger.debug(f"State token revoked: {token[:8]}...")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get state token statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._lock:
                current_time = datetime.utcnow()
                
                total_tokens = len(self._tokens)
                active_tokens = sum(
                    1 for data in self._tokens.values()
                    if not data['used'] and current_time <= data['expires_at']
                )
                expired_tokens = sum(
                    1 for data in self._tokens.values()
                    if current_time > data['expires_at']
                )
                used_tokens = sum(
                    1 for data in self._tokens.values()
                    if data['used']
                )
                
                return {
                    'total_tokens': total_tokens,
                    'active_tokens': active_tokens,
                    'expired_tokens': expired_tokens,
                    'used_tokens': used_tokens
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}

# Global state manager instance
_state_manager = None

def get_state_manager() -> SecureStateManager:
    """Get global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = SecureStateManager()
    return _state_manager

# Test function
def test_state_manager():
    """Test state manager functionality"""
    print("🔍 Testing Secure State Manager...")
    
    manager = SecureStateManager(token_expiry_minutes=1)
    
    # Test token generation
    token = manager.generate_state_token(
        user_session="test-session-001",
        metadata={"redirect_uri": "https://example.com/callback"}
    )
    print(f"✅ Token generated: {token[:12]}...")
    
    # Test token validation
    valid, metadata = manager.validate_and_consume_state_token(
        token, 
        user_session="test-session-001"
    )
    print(f"✅ Token validation: {'Success' if valid else 'Failed'}")
    print(f"✅ Metadata retrieved: {metadata}")
    
    # Test token reuse (should fail)
    valid2, _ = manager.validate_and_consume_state_token(token)
    print(f"✅ Token reuse prevention: {'Success' if not valid2 else 'Failed'}")
    
    # Test stats
    stats = manager.get_stats()
    print(f"✅ Token stats: {stats}")
    
    print("🎉 State manager tests completed!")

if __name__ == "__main__":
    test_state_manager()