"""
Google Pay Integration Service for AI Marketing Automation Platform
Handles subscription billing using Google Pay API
"""

import os
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from google.auth import default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import stripe
from dotenv import load_dotenv

load_dotenv()


class GooglePayService:
    """Service for Google Pay subscription management"""
    
    def __init__(self):
        # Google Pay Configuration
        self.google_pay_environment = os.getenv("GOOGLE_PAY_ENVIRONMENT", "TEST")  # TEST or PRODUCTION
        self.google_pay_gateway = os.getenv("GOOGLE_PAY_GATEWAY", "stripe")
        self.google_pay_gateway_merchant_id = os.getenv("GOOGLE_PAY_GATEWAY_MERCHANT_ID")
        self.google_pay_merchant_name = os.getenv("GOOGLE_PAY_MERCHANT_NAME", "AI Marketing Automation")
        
        # Stripe Configuration (for processing Google Pay tokens)
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # Google Cloud Configuration
        self.google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        
    def get_google_pay_config(self) -> Dict[str, Any]:
        """Get Google Pay configuration for frontend"""
        return {
            "environment": self.google_pay_environment,
            "apiVersion": 2,
            "apiVersionMinor": 0,
            "allowedPaymentMethods": [
                {
                    "type": "CARD",
                    "parameters": {
                        "allowedAuthMethods": ["PAN_ONLY", "CRYPTOGRAM_3DS"],
                        "allowedCardNetworks": ["MASTERCARD", "VISA", "AMEX"]
                    },
                    "tokenizationSpecification": {
                        "type": "PAYMENT_GATEWAY",
                        "parameters": {
                            "gateway": self.google_pay_gateway,
                            "gatewayMerchantId": self.google_pay_gateway_merchant_id
                        }
                    }
                }
            ],
            "merchantInfo": {
                "merchantName": self.google_pay_merchant_name,
                "merchantId": self.google_pay_gateway_merchant_id
            }
        }
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        customer_id: str = None,
        subscription_id: str = None,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a Stripe PaymentIntent for Google Pay token processing"""
        
        try:
            # Convert to cents for Stripe
            amount_cents = int(amount * 100)
            
            payment_intent_data = {
                "amount": amount_cents,
                "currency": currency.lower(),
                "payment_method_types": ["card"],
                "capture_method": "automatic"
            }
            
            if customer_id:
                payment_intent_data["customer"] = customer_id
            
            if metadata:
                payment_intent_data["metadata"] = metadata
                
            if subscription_id:
                if not metadata:
                    metadata = {}
                metadata["subscription_id"] = subscription_id
                payment_intent_data["metadata"] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            return {
                "success": True,
                "payment_intent": {
                    "id": payment_intent.id,
                    "client_secret": payment_intent.client_secret,
                    "amount": payment_intent.amount,
                    "currency": payment_intent.currency,
                    "status": payment_intent.status
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def confirm_payment_with_google_pay_token(
        self,
        payment_intent_id: str,
        google_pay_token: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Confirm payment using Google Pay token"""
        
        try:
            # Extract payment token from Google Pay response
            payment_data = google_pay_token.get("paymentMethodData", {})
            tokenization_data = payment_data.get("tokenizationData", {})
            
            if tokenization_data.get("type") != "PAYMENT_GATEWAY":
                return {
                    "success": False,
                    "error": "Invalid tokenization type",
                    "error_type": "validation_error"
                }
            
            # Get the token from tokenization data
            token_data = json.loads(tokenization_data.get("token", "{}"))
            
            # Confirm the PaymentIntent with the Google Pay token
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method_data={
                    "type": "card",
                    "card": {
                        "token": token_data.get("id")
                    }
                }
            )
            
            return {
                "success": True,
                "payment_intent": {
                    "id": payment_intent.id,
                    "status": payment_intent.status,
                    "amount": payment_intent.amount,
                    "currency": payment_intent.currency
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: str = None,
        trial_period_days: int = 14,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a Stripe subscription"""
        
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
            }
            
            if trial_period_days > 0:
                subscription_data["trial_period_days"] = trial_period_days
            
            if payment_method_id:
                subscription_data["default_payment_method"] = payment_method_id
            
            if metadata:
                subscription_data["metadata"] = metadata
            
            subscription = stripe.Subscription.create(**subscription_data)
            
            return {
                "success": True,
                "subscription": {
                    "id": subscription.id,
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start,
                    "current_period_end": subscription.current_period_end,
                    "trial_end": subscription.trial_end,
                    "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                "success": True,
                "subscription": {
                    "id": subscription.id,
                    "status": subscription.status,
                    "canceled_at": subscription.canceled_at
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def update_subscription(
        self,
        subscription_id: str,
        price_id: str = None,
        payment_method_id: str = None,
        proration_behavior: str = "create_prorations"
    ) -> Dict[str, Any]:
        """Update a subscription (upgrade/downgrade)"""
        
        try:
            update_data = {}
            
            if price_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                update_data["items"] = [{
                    "id": subscription["items"]["data"][0].id,
                    "price": price_id,
                }]
                update_data["proration_behavior"] = proration_behavior
            
            if payment_method_id:
                update_data["default_payment_method"] = payment_method_id
            
            subscription = stripe.Subscription.modify(subscription_id, **update_data)
            
            return {
                "success": True,
                "subscription": {
                    "id": subscription.id,
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start,
                    "current_period_end": subscription.current_period_end,
                    "items": [{"price": item.price.id, "quantity": item.quantity} for item in subscription.items.data]
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        
        if not self.webhook_secret:
            return False
        
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except ValueError:
            # Invalid payload
            return False
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return False
    
    def create_stripe_prices(self) -> Dict[str, str]:
        """Create Stripe prices for subscription tiers"""
        
        prices = {}
        
        subscription_tiers = {
            "starter": {
                "unit_amount": 4999,  # $49.99
                "nickname": "Starter Plan"
            },
            "professional": {
                "unit_amount": 14999,  # $149.99
                "nickname": "Professional Plan"
            },
            "enterprise": {
                "unit_amount": 39999,  # $399.99
                "nickname": "Enterprise Plan"
            }
        }
        
        for tier, config in subscription_tiers.items():
            try:
                price = stripe.Price.create(
                    unit_amount=config["unit_amount"],
                    currency="usd",
                    recurring={"interval": "month"},
                    product_data={
                        "name": f"AI Marketing Automation - {config['nickname']}",
                    },
                    nickname=config["nickname"],
                    metadata={"tier": tier}
                )
                prices[tier] = price.id
            except stripe.error.StripeError as e:
                print(f"Error creating price for {tier}: {e}")
                
        return prices
    
    async def create_customer(
        self,
        email: str,
        name: str = None,
        phone: str = None,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer"""
        
        try:
            customer_data = {"email": email}
            
            if name:
                customer_data["name"] = name
            
            if phone:
                customer_data["phone"] = phone
            
            if metadata:
                customer_data["metadata"] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            
            return {
                "success": True,
                "customer": {
                    "id": customer.id,
                    "email": customer.email,
                    "name": customer.name
                }
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def get_customer_subscriptions(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's subscriptions"""
        
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                limit=10
            )
            
            return {
                "success": True,
                "subscriptions": [
                    {
                        "id": sub.id,
                        "status": sub.status,
                        "current_period_start": sub.current_period_start,
                        "current_period_end": sub.current_period_end,
                        "trial_end": sub.trial_end,
                        "items": [
                            {
                                "price": item.price.id,
                                "quantity": item.quantity,
                                "amount": item.price.unit_amount
                            } for item in sub.items.data
                        ]
                    } for sub in subscriptions.data
                ]
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def get_customer_invoices(
        self, 
        customer_id: str, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get customer's invoices"""
        
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return {
                "success": True,
                "invoices": [
                    {
                        "id": invoice.id,
                        "number": invoice.number,
                        "status": invoice.status,
                        "amount_paid": invoice.amount_paid,
                        "amount_due": invoice.amount_due,
                        "currency": invoice.currency,
                        "created": invoice.created,
                        "period_start": invoice.period_start,
                        "period_end": invoice.period_end,
                        "hosted_invoice_url": invoice.hosted_invoice_url,
                        "invoice_pdf": invoice.invoice_pdf
                    } for invoice in invoices.data
                ]
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }


# Singleton instance
google_pay_service = GooglePayService()