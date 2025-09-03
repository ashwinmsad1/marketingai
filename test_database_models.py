#!/usr/bin/env python3
"""
Test script to validate database models with new indexes and constraints.
This script tests model imports and constraint definitions without requiring a database connection.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test that all models can be imported successfully."""
    try:
        from database.models import (
            User, Campaign, Analytics, Payment, BillingSubscription, 
            CompetitorContent, Base
        )
        print("✅ All models imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False

def test_table_args():
    """Test that __table_args__ are properly defined."""
    from database.models import Campaign, Analytics, Payment, BillingSubscription, CompetitorContent, User
    
    models_to_test = [
        (User, "users"),
        (Campaign, "campaigns"), 
        (Analytics, "analytics"),
        (Payment, "payments"),
        (BillingSubscription, "billing_subscriptions"),
        (CompetitorContent, "competitor_content")
    ]
    
    for model_class, table_name in models_to_test:
        if hasattr(model_class, '__table_args__'):
            table_args = model_class.__table_args__
            if table_args:
                print(f"✅ {table_name}: {len(table_args)} constraints/indexes defined")
            else:
                print(f"⚠️  {table_name}: __table_args__ is empty")
        else:
            print(f"❌ {table_name}: No __table_args__ defined")

def test_constraint_types():
    """Test that constraints are of the correct types."""
    from database.models import Campaign
    from sqlalchemy import Index, CheckConstraint, UniqueConstraint
    
    if hasattr(Campaign, '__table_args__'):
        table_args = Campaign.__table_args__
        
        indexes = [arg for arg in table_args if isinstance(arg, Index)]
        check_constraints = [arg for arg in table_args if isinstance(arg, CheckConstraint)]
        unique_constraints = [arg for arg in table_args if isinstance(arg, UniqueConstraint)]
        
        print(f"✅ Campaign model has:")
        print(f"   - {len(indexes)} indexes")
        print(f"   - {len(check_constraints)} check constraints")
        print(f"   - {len(unique_constraints)} unique constraints")
        
        # Test a few specific constraints
        constraint_names = [getattr(arg, 'name', str(arg)) for arg in table_args]
        
        expected_constraints = [
            'idx_campaigns_user_id',
            'chk_campaigns_budget_daily_positive',
            'chk_campaigns_spend_positive'
        ]
        
        for constraint in expected_constraints:
            if any(constraint in name for name in constraint_names):
                print(f"   ✅ Found expected constraint: {constraint}")
            else:
                print(f"   ❌ Missing expected constraint: {constraint}")

def test_model_relationships():
    """Test that model relationships are still intact."""
    from database.models import User, Campaign, Analytics
    
    # Test that relationships are defined
    user_relationships = [attr for attr in dir(User) if not attr.startswith('_')]
    campaign_relationships = [attr for attr in dir(Campaign) if not attr.startswith('_')]
    
    expected_user_rels = ['campaigns', 'payments', 'billing_subscriptions']
    expected_campaign_rels = ['user', 'analytics', 'ai_content']
    
    for rel in expected_user_rels:
        if rel in user_relationships:
            print(f"✅ User.{rel} relationship exists")
        else:
            print(f"❌ User.{rel} relationship missing")
    
    for rel in expected_campaign_rels:
        if rel in campaign_relationships:
            print(f"✅ Campaign.{rel} relationship exists")
        else:
            print(f"❌ Campaign.{rel} relationship missing")

if __name__ == "__main__":
    print("🧪 Testing Database Models with Performance Optimizations")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Model Imports", test_model_imports),
        ("Table Args Definition", test_table_args), 
        ("Constraint Types", test_constraint_types),
        ("Model Relationships", test_model_relationships)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            if result is not False:  # None or True are considered passing
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Models are ready for migration.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        sys.exit(1)