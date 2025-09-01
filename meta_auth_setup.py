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
from urllib.parse import urlencode, parse_qs
from typing import Dict, Optional, List
from datetime import datetime, timedelta

class MetaAPIAuthenticator:
    """
    Handles Meta API authentication flow and token management
    """
    
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/callback")
        
        # Meta API endpoints
        self.auth_base_url = "https://www.facebook.com/v19.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        self.graph_api_url = "https://graph.facebook.com/v19.0"
        
        if not all([self.app_id, self.app_secret]):
            raise ValueError("FACEBOOK_APP_ID and FACEBOOK_APP_SECRET must be set in environment variables")
    
    def generate_auth_url(self, scopes: List[str] = None) -> tuple[str, str]:
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
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"{self.auth_base_url}?{urlencode(params)}"
        return auth_url, state
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict with access token and expiration info
        """
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
                    error_data = await response.json()
                    raise Exception(f"Token exchange failed: {error_data}")
    
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
                    error_data = await response.json()
                    raise Exception(f"Long-lived token exchange failed: {error_data}")
    
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
                    error_data = await response.json()
                    raise Exception(f"Failed to get user info: {error_data}")
    
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
                    error_data = await response.json()
                    raise Exception(f"Failed to get ad accounts: {error_data}")
    
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
                    error_data = await response.json()
                    raise Exception(f"Failed to get pages: {error_data}")
    
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
                    error_data = await response.json()
                    raise Exception(f"Token validation failed: {error_data}")

class UserOnboardingFlow:
    """
    Complete user onboarding flow for Meta API integration
    """
    
    def __init__(self):
        self.authenticator = MetaAPIAuthenticator()
    
    async def start_onboarding(self) -> Dict[str, any]:
        """
        Start the complete onboarding process
        """
        print("🚀 Starting Meta API Onboarding Process")
        print("=" * 50)
        
        # Step 1: Generate authorization URL
        auth_url, state = self.authenticator.generate_auth_url()
        
        print(f"📱 Step 1: Facebook Authorization")
        print(f"Please visit the following URL to authorize the application:")
        print(f"\n{auth_url}\n")
        
        # Optionally open browser automatically
        if input("Open browser automatically? (y/n): ").lower().strip() == 'y':
            webbrowser.open(auth_url)
        
        # Step 2: Get authorization code
        print("\n📝 Step 2: Authorization Code")
        print("After authorizing, you'll be redirected to a URL containing a 'code' parameter.")
        code = input("Enter the authorization code: ").strip()
        
        try:
            # Step 3: Exchange code for token
            print("\n🔐 Step 3: Token Exchange")
            token_data = await self.authenticator.exchange_code_for_token(code)
            print("✅ Successfully obtained access token!")
            
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
                
        except Exception as e:
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
            
        except Exception as e:
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
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())