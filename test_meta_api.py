#!/usr/bin/env python3
"""
Quick test script to verify Meta API connectivity
Run: python test_meta_api.py
"""

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User
import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_meta_api_connection():
    """Test basic Meta API connectivity"""
    
    # Load access token from environment
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No access token provided")
        return False
        
    try:
        # Initialize the Facebook API
        FacebookAdsApi.init(access_token=access_token)
        
        # Test basic API call - get current user info
        me = User(fbid='me')
        my_data = me.api_get(fields=['id', 'name'])
        
        print(f"✅ API Connection Successful!")
        print(f"User ID: {my_data.get('id')}")
        print(f"Name: {my_data.get('name')}")
        
        # Test available permissions
        try:
            ad_accounts = me.get_ad_accounts(fields=['id', 'name', 'account_status'])
            if ad_accounts:
                print(f"\n📊 Found {len(ad_accounts)} ad account(s):")
                for account in ad_accounts:
                    print(f"  - {account.get('name')} (ID: {account.get('id')}) - Status: {account.get('account_status')}")
            else:
                print("\n⚠️  No ad accounts found.")
        except Exception as e:
            print(f"\n⚠️  Ad accounts access failed: {str(e)}")
            print("This is expected - you need ads permissions for Marketing API")
            
        # Test pages access (you have this permission)
        try:
            pages = me.get_accounts(fields=['id', 'name', 'access_token'])
            if pages:
                print(f"\n📄 Found {len(pages)} page(s):")
                for page in pages:
                    print(f"  - {page.get('name')} (ID: {page.get('id')})")
            else:
                print("\n📄 No pages found.")
        except Exception as e:
            print(f"\n⚠️  Pages access failed: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"❌ API Connection Failed: {str(e)}")
        print("\nCommon issues:")
        print("1. Invalid access token")
        print("2. Token doesn't have required permissions")
        print("3. App not approved for Marketing API")
        print("4. Network connectivity issues")
        return False

def test_conversions_api():
    """Test Conversions API (Server-Side Events)"""
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    app_id = os.getenv('FACEBOOK_APP_ID')
    
    # You'll need a pixel ID - for testing we'll create a dummy one
    pixel_id = "123456789"  # Replace with actual pixel ID when available
    
    print("\n🎯 Testing Conversions API (Server-Side Events)...")
    print("=" * 50)
    
    # Sample conversion event data
    event_data = {
        "data": [
            {
                "event_name": "Purchase",
                "event_time": int(time.time()),
                "action_source": "website",
                "user_data": {
                    "em": ["test@example.com"],  # hashed email would be better
                    "client_ip_address": "192.168.1.1",
                    "client_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                },
                "custom_data": {
                    "currency": "INR",
                    "value": 2999.00,
                    "content_name": "Professional Tier Subscription",
                    "content_category": "SaaS Subscription"
                }
            }
        ],
        "test_event_code": "TEST12345"  # For testing only
    }
    
    url = f"https://graph.facebook.com/v20.0/{pixel_id}/events"
    
    params = {
        'access_token': access_token,
    }
    
    try:
        response = requests.post(url, params=params, json=event_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversions API Test Successful!")
            print(f"Events Received: {result.get('events_received', 0)}")
            print(f"Messages: {result.get('messages', [])}")
        else:
            print(f"❌ Conversions API Test Failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Conversions API Error: {str(e)}")
        
    print("\nNote: This test requires:")
    print("1. A valid Facebook Pixel ID")
    print("2. Proper permissions for Conversions API")
    print("3. App approved for Advanced Access")

if __name__ == "__main__":
    print("🔗 Testing Meta API Connection...")
    print("=" * 50)
    test_meta_api_connection()
    test_conversions_api()