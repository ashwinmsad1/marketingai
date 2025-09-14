"""
Standardized response formatter for all Meta API integrations
Provides consistent error and success response formats across Facebook Agent and Meta Ads Automation
"""
from typing import Dict, Any, Optional, List
from enum import Enum


class MetaErrorType(Enum):
    """Enumeration of Meta API error types"""
    RATE_LIMIT = "RATE_LIMIT"
    AUTH_ERROR = "AUTH_ERROR" 
    PERMISSION_ERROR = "PERMISSION_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    CLIENT_ERROR = "CLIENT_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UPLOAD_ERROR = "UPLOAD_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class MetaPlatform(Enum):
    """Enumeration of Meta platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    BOTH = "both"
    META_ADS = "meta_ads"


class MetaResponseFormatter:
    """Standardized response formatter for Meta API operations"""
    
    @staticmethod
    def success_response(
        platform: str,
        post_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            platform: Platform name (facebook, instagram, meta_ads, both)
            post_id: Optional post/content ID
            campaign_id: Optional campaign ID
            data: Optional additional data
            message: Optional success message
        
        Returns:
            Standardized success response dictionary
        """
        response = {
            'success': True,
            'platform': platform,
            'post_id': post_id,
            'campaign_id': campaign_id,
            'error': None,
            'error_type': None,
            'retry_suggested': False,
            'timestamp': None  # Will be set by caller if needed
        }
        
        if data:
            response['data'] = data
        
        if message:
            response['message'] = message
            
        return response
    
    @staticmethod
    def error_response(
        platform: str,
        error_message: str,
        error_type: MetaErrorType,
        retry_suggested: bool = False,
        post_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            platform: Platform name (facebook, instagram, meta_ads, both)
            error_message: Error description
            error_type: Type of error (MetaErrorType enum)
            retry_suggested: Whether retry is recommended
            post_id: Optional post/content ID (if partially successful)
            campaign_id: Optional campaign ID (if partially successful)
            data: Optional additional error data
        
        Returns:
            Standardized error response dictionary
        """
        return {
            'success': False,
            'platform': platform,
            'post_id': post_id,
            'campaign_id': campaign_id,
            'error': error_message,
            'error_type': error_type.value,
            'retry_suggested': retry_suggested,
            'timestamp': None,  # Will be set by caller if needed
            'data': data or {}
        }
    
    @staticmethod
    def batch_response(
        platform: str,
        results: List[Dict[str, Any]],
        overall_success: bool = None
    ) -> Dict[str, Any]:
        """
        Create standardized batch operation response
        
        Args:
            platform: Platform name
            results: List of individual operation results
            overall_success: Override overall success status
        
        Returns:
            Standardized batch response dictionary
        """
        if overall_success is None:
            overall_success = all(result.get('success', False) for result in results)
        
        successful_count = sum(1 for result in results if result.get('success', False))
        failed_count = len(results) - successful_count
        
        return {
            'success': overall_success,
            'platform': platform,
            'batch_results': results,
            'total_operations': len(results),
            'successful_operations': successful_count,
            'failed_operations': failed_count,
            'error': None if overall_success else f"{failed_count}/{len(results)} operations failed",
            'error_type': None if overall_success else MetaErrorType.UNKNOWN_ERROR.value,
            'retry_suggested': failed_count > 0 and any(
                result.get('retry_suggested', False) for result in results if not result.get('success', False)
            )
        }
    
    @staticmethod
    def campaign_response(
        campaign_id: Optional[str],
        adset_ids: List[str] = None,
        ad_ids: List[str] = None,
        creative_ids: List[str] = None,
        platforms: List[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        error_type: Optional[MetaErrorType] = None
    ) -> Dict[str, Any]:
        """
        Create standardized campaign creation response
        
        Args:
            campaign_id: Created campaign ID
            adset_ids: List of created adset IDs
            ad_ids: List of created ad IDs
            creative_ids: List of created creative IDs
            platforms: List of platforms used
            success: Whether operation succeeded
            error: Error message if failed
            error_type: Type of error if failed
        
        Returns:
            Standardized campaign response dictionary
        """
        return {
            'success': success,
            'platform': MetaPlatform.META_ADS.value,
            'campaign_id': campaign_id,
            'adset_ids': adset_ids or [],
            'ad_ids': ad_ids or [],
            'creative_ids': creative_ids or [],
            'total_ads_created': len(ad_ids) if ad_ids else 0,
            'platforms': platforms or [],
            'error': error,
            'error_type': error_type.value if error_type else None,
            'retry_suggested': error_type in [
                MetaErrorType.RATE_LIMIT, 
                MetaErrorType.NETWORK_ERROR, 
                MetaErrorType.SERVER_ERROR
            ] if error_type else False
        }


def classify_meta_error(error: Exception) -> tuple[MetaErrorType, bool, float]:
    """
    Classify Meta API errors and determine retry strategy
    
    Args:
        error: Exception to classify
    
    Returns:
        tuple: (error_type, should_retry, delay_seconds)
    """
    error_str = str(error).lower()
    
    # Rate limit errors
    if 'rate limit' in error_str or 'too many calls' in error_str or '613' in error_str:
        return MetaErrorType.RATE_LIMIT, True, 60.0
    
    # Authentication errors
    if 'access token' in error_str or 'invalid token' in error_str or 'expired' in error_str:
        return MetaErrorType.AUTH_ERROR, False, 0.0
    
    # Permission errors
    if 'permission' in error_str or 'forbidden' in error_str or '403' in error_str:
        return MetaErrorType.PERMISSION_ERROR, False, 0.0
    
    # Upload errors
    if 'upload' in error_str or 'file' in error_str or 'media' in error_str:
        return MetaErrorType.UPLOAD_ERROR, True, 2.0
    
    # Network/temporary errors
    if 'timeout' in error_str or 'connection' in error_str or 'network' in error_str:
        return MetaErrorType.NETWORK_ERROR, True, 2.0
    
    # Server errors (5xx)
    if '500' in error_str or '502' in error_str or '503' in error_str or '504' in error_str:
        return MetaErrorType.SERVER_ERROR, True, 5.0
    
    # Client errors (4xx) - usually don't retry
    if '400' in error_str or '404' in error_str or '422' in error_str:
        return MetaErrorType.CLIENT_ERROR, False, 0.0
    
    # Validation errors
    if 'invalid' in error_str or 'validation' in error_str or 'required' in error_str:
        return MetaErrorType.VALIDATION_ERROR, False, 0.0
    
    # Unknown errors - retry with caution
    return MetaErrorType.UNKNOWN_ERROR, True, 1.0