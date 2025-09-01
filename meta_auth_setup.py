"""
Meta API Authentication and User Onboarding System
Handles OAuth flow, token management, and user setup for Meta Marketing API
"""

import os
import asyncio
import aiohttp
import json
import secrets
import webbrowser
import logging
from urllib.parse import urlencode, parse_qs
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from secure_state_manager import (
    SecureStateManager, StateTokenError, StateTokenExpiredError, 
    StateTokenInvalidError, generate_oauth_state, validate_oauth_state
)
from secure_config_manager import get_config, ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)

class MetaAPIAuthenticator:
    """
    Handles Meta API authentication flow and token management
    """
    
    def __init__(self):
        try:
            self.app_id = get_config("FACEBOOK_APP_ID")
            self.app_secret = get_config("FACEBOOK_APP_SECRET")
            self.redirect_uri = get_config("FACEBOOK_REDIRECT_URI")
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            raise ValueError(f"Meta API configuration error: {e}")
        
        # Initialize secure state manager
        self.state_manager = SecureStateManager()
        
        # Meta API endpoints
        self.auth_base_url = "https://www.facebook.com/v19.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        self.graph_api_url = "https://graph.facebook.com/v19.0"
        
        logger.info("Meta API Authenticator initialized successfully")
    
    def generate_auth_url(self, scopes: List[str] = None, user_session: Optional[str] = None) -> tuple[str, str]:
        """
        Generate Facebook OAuth URL for user authorization
        
        Args:
            scopes: List of permissions to request
            
        Returns:
            tuple: (auth_url, state) for CSRF protection
        """
        if scopes is None:
            scopes = [
                'ads_management',           # Create and manage ads
                'ads_read',                # Read ad account data
                'read_insights',           # Access analytics
                'pages_manage_posts',      # Manage Facebook pages
                'instagram_basic',         # Access Instagram account
                'instagram_content_publish' # Publish to Instagram
            ]
        
        # Generate secure state token for CSRF protection
        try:
            state, state_hash = self.state_manager.generate_state_token(
                user_session=user_session,
                metadata={
                    'scopes': scopes,
                    'redirect_uri': self.redirect_uri,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.info(f"Generated OAuth state token: {state[:8]}...")
        except StateTokenError as e:
            logger.error(f"Failed to generate state token: {e}")
            raise ValueError(f"State token generation failed: {e}")
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"{self.auth_base_url}?{urlencode(params)}"
        return auth_url, state
    
    async def exchange_code_for_token(self, code: str, state_token: Optional[str] = None, 
                                     user_session: Optional[str] = None) -> Dict[str, any]:
        """
        Exchange authorization code for access token with state validation
        
        Args:
            code: Authorization code from callback
            state_token: State token for CSRF protection
            user_session: Optional user session identifier
            
        Returns:
            Dict with access token and expiration info
        
        Raises:
            ValueError: If code is invalid or state validation fails
        """
        # Validate state token if provided
        if state_token:
            try:
                validation_result = self.state_manager.validate_state_token(state_token, user_session)
                logger.info(f"State token validated successfully for OAuth exchange")
            except (StateTokenExpiredError, StateTokenInvalidError) as e:
                logger.error(f"State token validation failed: {e}")
                raise ValueError(f"Invalid OAuth state: {e}")
            except StateTokenError as e:
                logger.error(f"State token error: {e}")
                raise ValueError(f"State validation error: {e}")
        
        if not code:
            raise ValueError("Authorization code is required")
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.token_url, params=params) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Exchange short-lived token for long-lived token
                    long_lived_token = await self.get_long_lived_token(token_data['access_token'])
                    
                    return {
                        'access_token': long_lived_token['access_token'],
                        'token_type': 'long_lived',
                        'expires_in': long_lived_token.get('expires_in', 5184000),  # ~60 days
                        'expires_at': datetime.now() + timedelta(seconds=long_lived_token.get('expires_in', 5184000))
                    }
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Token exchange failed: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Token exchange failed: {error_msg}")
    
    async def get_long_lived_token(self, short_token: str) -> Dict[str, any]:
        """Convert short-lived token to long-lived token"""
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.token_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Long-lived token exchange failed: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Long-lived token exchange failed: {error_msg}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """Get user information and permissions"""
        params = {
            'access_token': access_token,
            'fields': 'id,name,email'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.graph_api_url}/me", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Failed to get user info: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Failed to get user info: {error_msg}")
    
    async def get_user_ad_accounts(self, access_token: str) -> List[Dict[str, any]]:
        """Get user's advertising accounts"""
        params = {
            'access_token': access_token,
            'fields': 'account_id,name,account_status,currency,timezone_name'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.graph_api_url}/me/adaccounts", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Failed to get ad accounts: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Failed to get ad accounts: {error_msg}")
    
    async def get_user_pages(self, access_token: str) -> List[Dict[str, any]]:
        """Get user's Facebook pages"""
        params = {
            'access_token': access_token,
            'fields': 'id,name,category,instagram_business_account'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.graph_api_url}/me/accounts", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Failed to get pages: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Failed to get pages: {error_msg}")
    
    async def validate_token(self, access_token: str) -> Dict[str, any]:
        """Validate access token and check permissions"""
        params = {
            'input_token': access_token,
            'access_token': f"{self.app_id}|{self.app_secret}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.graph_api_url}/debug_token", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {})
                else:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = await response.text()
                    logger.error(f"Token validation failed: HTTP {response.status} - {error_msg}")
                    raise ValueError(f"Token validation failed: {error_msg}")

class UserOnboardingFlow:
    """
    Complete user onboarding flow for Meta API integration
    """
    
    def __init__(self):
        self.authenticator = MetaAPIAuthenticator()
        self._current_session_id = None
    
    async def start_onboarding(self) -> Dict[str, any]:
        """
        Start the complete onboarding process
        """
        print("🚀 Starting Meta API Onboarding Process")
        print("=" * 50)
        
        # Generate session ID for state tracking
        self._current_session_id = secrets.token_urlsafe(16)
        logger.info(f"Starting onboarding session: {self._current_session_id}")
        
        # Step 1: Generate authorization URL with secure state
        auth_url, state = self.authenticator.generate_auth_url(
            user_session=self._current_session_id
        )
        self._current_state_token = state
        
        print(f"📱 Step 1: Facebook Authorization")
        print(f"Please visit the following URL to authorize the application:")
        print(f"\n{auth_url}\n")
        
        # Optionally open browser automatically
        if input("Open browser automatically? (y/n): ").lower().strip() == 'y':
            webbrowser.open(auth_url)
        
        # Step 2: Get authorization code and state validation
        print("\n📝 Step 2: Authorization Code")
        print("After authorizing, you'll be redirected to a URL containing 'code' and 'state' parameters.")
        callback_url = input("Enter the full callback URL (or just the authorization code): ").strip()
        
        # Parse callback URL or use as direct code
        if callback_url.startswith('http'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(callback_url)
            query_params = parse_qs(parsed.query)
            code = query_params.get('code', [None])[0]
            returned_state = query_params.get('state', [None])[0]
            
            if returned_state != state:
                logger.error("State mismatch in OAuth callback")
                raise ValueError("Invalid OAuth state - possible CSRF attack")
        else:
            code = callback_url
            returned_state = state  # Assume state is correct for direct code entry
        
        if not code:
            raise ValueError("Authorization code not found")
        
        try:
            # Step 3: Exchange code for token with state validation
            print("\n🔐 Step 3: Token Exchange")
            token_data = await self.authenticator.exchange_code_for_token(
                code, 
                state_token=returned_state, 
                user_session=self._current_session_id
            )
            print("✅ Successfully obtained access token with state validation!")
            
            # Step 4: Get user information
            print("\n👤 Step 4: User Information")
            user_info = await self.authenticator.get_user_info(token_data['access_token'])
            print(f"✅ Welcome, {user_info['name']}! (ID: {user_info['id']})")
            
            # Step 5: Get ad accounts
            print("\n💼 Step 5: Ad Accounts Discovery")
            ad_accounts = await self.authenticator.get_user_ad_accounts(token_data['access_token'])
            
            if not ad_accounts:
                print("❌ No ad accounts found. You need a Facebook Ads account to continue.")
                return {'success': False, 'error': 'No ad accounts available'}
            
            print(f"✅ Found {len(ad_accounts)} ad account(s):")
            for i, account in enumerate(ad_accounts):
                print(f"  {i+1}. {account['name']} (ID: {account['account_id']})")
            
            # Let user select ad account
            if len(ad_accounts) == 1:
                selected_account = ad_accounts[0]
                print(f"✅ Auto-selected: {selected_account['name']}")
            else:
                selection = int(input(f"\nSelect ad account (1-{len(ad_accounts)}): ")) - 1
                selected_account = ad_accounts[selection]
                print(f"✅ Selected: {selected_account['name']}")
            
            # Step 6: Get Facebook pages
            print("\n📄 Step 6: Facebook Pages Discovery")
            pages = await self.authenticator.get_user_pages(token_data['access_token'])
            
            if not pages:
                print("❌ No Facebook pages found. You need a Facebook page to post content.")
                return {'success': False, 'error': 'No Facebook pages available'}
            
            print(f"✅ Found {len(pages)} page(s):")
            instagram_pages = []
            for i, page in enumerate(pages):
                instagram_status = "✅ Instagram Connected" if page.get('instagram_business_account') else "❌ No Instagram"
                print(f"  {i+1}. {page['name']} - {instagram_status}")
                if page.get('instagram_business_account'):
                    instagram_pages.append(page)
            
            # Let user select page
            if len(pages) == 1:
                selected_page = pages[0]
                print(f"✅ Auto-selected: {selected_page['name']}")
            else:
                selection = int(input(f"\nSelect Facebook page (1-{len(pages)}): ")) - 1
                selected_page = pages[selection]
                print(f"✅ Selected: {selected_page['name']}")
            
            # Step 7: Generate environment configuration
            print("\n⚙️  Step 7: Environment Configuration")
            env_config = self._generate_env_config(
                token_data,
                user_info,
                selected_account,
                selected_page
            )
            
            # Save to .env file
            self._save_env_config(env_config)
            print("✅ Configuration saved to .env file!")
            
            # Step 8: Validation
            print("\n🔍 Step 8: Setup Validation")
            validation_result = await self._validate_setup(token_data['access_token'])
            
            if validation_result['success']:
                print("🎉 Onboarding completed successfully!")
                print("\n📋 Setup Summary:")
                print(f"  👤 User: {user_info['name']}")
                print(f"  💼 Ad Account: {selected_account['name']}")
                print(f"  📄 Facebook Page: {selected_page['name']}")
                instagram_status = "✅ Connected" if selected_page.get('instagram_business_account') else "❌ Not Connected"
                print(f"  📸 Instagram: {instagram_status}")
                print(f"  🔐 Token Expires: {token_data['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                return {
                    'success': True,
                    'user_info': user_info,
                    'ad_account': selected_account,
                    'facebook_page': selected_page,
                    'token_info': token_data,
                    'instagram_connected': bool(selected_page.get('instagram_business_account'))
                }
            else:
                print(f"❌ Setup validation failed: {validation_result['error']}")
                return {'success': False, 'error': validation_result['error']}
                
        except ValueError as e:
            logger.error(f"Validation error in onboarding: {e}")
            print(f"❌ Validation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in onboarding: {e}")
            print(f"❌ Onboarding failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_env_config(self, token_data: Dict, user_info: Dict, ad_account: Dict, page: Dict) -> Dict[str, str]:
        """Generate environment configuration"""
        config = {
            'META_ACCESS_TOKEN': token_data['access_token'],
            'META_AD_ACCOUNT_ID': ad_account['account_id'].replace('act_', ''),
            'FACEBOOK_PAGE_ID': page['id'],
            'META_USER_ID': user_info['id'],
            'META_USER_NAME': user_info['name'],
            'TOKEN_EXPIRES_AT': token_data['expires_at'].isoformat()
        }
        
        # Add Instagram Business Account ID if available
        if page.get('instagram_business_account'):
            config['INSTAGRAM_BUSINESS_ID'] = page['instagram_business_account']['id']
        
        return config
    
    def _save_env_config(self, config: Dict[str, str]):
        """Save configuration to .env file"""
        env_path = '.env'
        
        # Read existing .env if it exists
        existing_config = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing_config[key] = value
        
        # Update with new config
        existing_config.update(config)
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.write("# Meta Marketing API Configuration\n")
            f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in existing_config.items():
                f.write(f"{key}={value}\n")
    
    async def _validate_setup(self, access_token: str) -> Dict[str, any]:
        """Validate the complete setup"""
        try:
            # Validate token
            token_info = await self.authenticator.validate_token(access_token)
            
            required_permissions = ['ads_management', 'ads_read', 'read_insights']
            available_permissions = token_info.get('scopes', [])
            
            missing_permissions = [perm for perm in required_permissions if perm not in available_permissions]
            
            if missing_permissions:
                return {
                    'success': False,
                    'error': f'Missing required permissions: {", ".join(missing_permissions)}'
                }
            
            return {'success': True, 'message': 'All validations passed'}
            
        except ValueError as e:
            logger.error(f"Token validation error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in token validation: {e}")
            return {'success': False, 'error': str(e)}

async def main():
    """
    Interactive onboarding flow
    """
    print("🤖 Meta Marketing API - User Onboarding")
    print("=" * 45)
    print("\nThis setup wizard will help you:")
    print("✅ Authenticate with Facebook/Meta")
    print("✅ Select your ad account and Facebook page")
    print("✅ Connect Instagram business account")
    print("✅ Configure environment variables")
    print("✅ Validate your setup")
    
    if input("\nReady to start? (y/n): ").lower().strip() != 'y':
        print("Setup cancelled.")
        return
    
    try:
        onboarding = UserOnboardingFlow()
        result = await onboarding.start_onboarding()
        
        if result['success']:
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install facebook-business")
            print("2. Test your setup: python meta_ads_automation.py")
            print("3. Create your first AI-powered ad campaign!")
        else:
            print(f"\n❌ Setup failed: {result['error']}")
            print("\nPlease check your configuration and try again.")
            
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except ValueError as e:
        logger.error(f"Validation error in main: {e}")
        print(f"\n❌ Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())