"""
Meta (Facebook/Instagram) account integration API routes
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from database.models import User, MetaAccount
from database.crud import UserCRUD
from auth.jwt_handler import get_current_active_user
from auth.models import MessageResponse
import os
import secrets
import logging
from typing import Dict, Any
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/meta", tags=["Meta Integration"])

# Meta OAuth Configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:3000/meta/callback")

class MetaOAuthHandler:
    """Handle Meta OAuth flow"""
    
    @staticmethod
    def generate_oauth_url(state: str) -> str:
        """Generate Meta OAuth authorization URL"""
        params = {
            'client_id': FACEBOOK_APP_ID,
            'redirect_uri': FACEBOOK_REDIRECT_URI,
            'scope': 'ads_management,ads_read,read_insights,pages_manage_posts,instagram_content_publish,business_management',
            'response_type': 'code',
            'state': state
        }
        
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        return f"{base_url}?{urlencode(params)}"
    
    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            'client_id': FACEBOOK_APP_ID,
            'client_secret': FACEBOOK_APP_SECRET,
            'redirect_uri': FACEBOOK_REDIRECT_URI,
            'code': code
        }
        
        response = requests.get(token_url, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token"
            )
        
        return response.json()
    
    @staticmethod
    def get_long_lived_token(short_token: str) -> Dict[str, Any]:
        """Convert short-lived token to long-lived token"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': FACEBOOK_APP_ID,
            'client_secret': FACEBOOK_APP_SECRET,
            'fb_exchange_token': short_token
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get long-lived token"
            )
        
        return response.json()
    
    @staticmethod
    def get_user_accounts(access_token: str) -> Dict[str, Any]:
        """Get user's ad accounts, pages, and Instagram accounts"""
        # Get ad accounts
        ad_accounts_url = f"https://graph.facebook.com/v18.0/me/adaccounts"
        ad_accounts_params = {
            'access_token': access_token,
            'fields': 'id,name,currency,timezone_name,account_status'
        }
        
        ad_accounts_response = requests.get(ad_accounts_url, params=ad_accounts_params)
        if ad_accounts_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch ad accounts"
            )
        
        # Get Facebook pages
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
        pages_params = {
            'access_token': access_token,
            'fields': 'id,name,category,access_token,instagram_business_account'
        }
        
        pages_response = requests.get(pages_url, params=pages_params)
        if pages_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch Facebook pages"
            )
        
        return {
            'ad_accounts': ad_accounts_response.json().get('data', []),
            'pages': pages_response.json().get('data', [])
        }

@router.get("/connect/start")
async def start_meta_connection(
    current_user: User = Depends(get_current_active_user)
):
    """Start Meta OAuth connection process"""
    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Meta app credentials not configured"
        )
    
    # Generate secure state parameter
    state = secrets.token_urlsafe(32)
    
    # Store state in user session (you might want to use database or cache)
    # For now, we'll return it and expect frontend to handle it
    
    oauth_url = MetaOAuthHandler.generate_oauth_url(state)
    
    return {
        'oauth_url': oauth_url,
        'state': state,
        'message': 'Redirect user to oauth_url to begin Meta account connection'
    }

@router.post("/connect/callback")
async def meta_oauth_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Handle Meta OAuth callback and save account"""
    try:
        # Exchange code for token
        token_data = MetaOAuthHandler.exchange_code_for_token(code)
        short_token = token_data['access_token']
        
        # Get long-lived token
        long_lived_data = MetaOAuthHandler.get_long_lived_token(short_token)
        access_token = long_lived_data['access_token']
        expires_in = long_lived_data.get('expires_in', 5184000)  # Default 60 days
        
        # Get user's accounts
        accounts_data = MetaOAuthHandler.get_user_accounts(access_token)
        
        # Save each ad account as a separate MetaAccount record
        created_accounts = []
        
        for ad_account in accounts_data['ad_accounts']:
            # Find associated Facebook page and Instagram account
            associated_page = None
            instagram_account_id = None
            
            for page in accounts_data['pages']:
                if page.get('instagram_business_account'):
                    associated_page = page
                    instagram_account_id = page['instagram_business_account']['id']
                    break
            
            # Create MetaAccount record
            meta_account = MetaAccount(
                user_id=current_user.id,
                access_token=access_token,  # Should encrypt in production
                app_id=FACEBOOK_APP_ID,
                app_secret=FACEBOOK_APP_SECRET,  # Should encrypt in production
                ad_account_id=ad_account['id'],
                facebook_page_id=associated_page['id'] if associated_page else None,
                instagram_business_id=instagram_account_id,
                account_name=ad_account['name'],
                currency=ad_account.get('currency', 'USD'),
                timezone=ad_account.get('timezone_name', 'UTC'),
                is_active=ad_account.get('account_status') == 1,
                # token_expires_at would be calculated from expires_in
            )
            
            db.add(meta_account)
            created_accounts.append({
                'ad_account_id': ad_account['id'],
                'name': ad_account['name'],
                'currency': ad_account.get('currency'),
                'page_name': associated_page['name'] if associated_page else None,
                'instagram_connected': instagram_account_id is not None
            })
        
        db.commit()
        
        logger.info(f"Meta accounts connected for user {current_user.email}: {len(created_accounts)} accounts")
        
        return {
            'message': f'Successfully connected {len(created_accounts)} Meta account(s)',
            'accounts': created_accounts,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Meta OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Meta account: {str(e)}"
        )

@router.get("/accounts")
async def get_connected_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's connected Meta accounts"""
    accounts = db.query(MetaAccount).filter(
        MetaAccount.user_id == current_user.id
    ).all()
    
    return {
        'accounts': [
            {
                'id': account.id,
                'ad_account_id': account.ad_account_id,
                'account_name': account.account_name,
                'currency': account.currency,
                'timezone': account.timezone,
                'facebook_page_id': account.facebook_page_id,
                'instagram_business_id': account.instagram_business_id,
                'is_active': account.is_active,
                'created_at': account.created_at.isoformat(),
                'last_sync': account.last_sync.isoformat() if account.last_sync else None
            }
            for account in accounts
        ],
        'total': len(accounts)
    }

@router.delete("/accounts/{account_id}")
async def disconnect_meta_account(
    account_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disconnect a Meta account"""
    account = db.query(MetaAccount).filter(
        MetaAccount.id == account_id,
        MetaAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta account not found"
        )
    
    db.delete(account)
    db.commit()
    
    logger.info(f"Meta account disconnected: {account.account_name} for user {current_user.email}")
    
    return MessageResponse(
        message="Meta account disconnected successfully",
        success=True
    )

@router.post("/accounts/{account_id}/refresh")
async def refresh_meta_token(
    account_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Refresh Meta account access token"""
    account = db.query(MetaAccount).filter(
        MetaAccount.id == account_id,
        MetaAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta account not found"
        )
    
    try:
        # Get new long-lived token
        long_lived_data = MetaOAuthHandler.get_long_lived_token(account.access_token)
        
        # Update account with new token
        account.access_token = long_lived_data['access_token']
        # account.token_expires_at = calculate_expiry_date(long_lived_data.get('expires_in'))
        
        db.commit()
        
        return MessageResponse(
            message="Meta account token refreshed successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Failed to refresh Meta token for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh Meta account token"
        )