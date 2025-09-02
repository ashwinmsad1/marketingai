"""
Payment Processing API Routes for Google Pay Integration
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging
from database import get_db
from database.models import User, SubscriptionTier, PaymentProvider, PaymentStatus, Payment, BillingSubscription
from database.payment_crud import (
    BillingSubscriptionCRUD, PaymentCRUD, InvoiceCRUD, 
    PaymentMethodCRUD, WebhookEventCRUD
)
from upi_payment_service import upi_payment_service
from subscription_management import PlatformSubscriptionManager
from google_pay_service import google_pay_service
from auth import get_current_active_user
from auth.jwt_handler import get_current_active_verified_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Pydantic models for API requests
class CreateSubscriptionRequest(BaseModel):
    tier: str = Field(..., description="Subscription tier: starter, professional, enterprise")
    trial_days: int = Field(30, description="Trial period in days")

class UPIPaymentRequest(BaseModel):
    payment_id: str = Field(..., description="UPI payment ID from gateway")
    order_id: str = Field(..., description="Order ID from payment gateway")
    signature: str = Field(None, description="Payment signature for verification")
    subscription_id: str = Field(..., description="Subscription ID to activate")

class UpdatePaymentMethodRequest(BaseModel):
    upi_id: str = Field(..., description="UPI ID/VPA")
    is_default: bool = Field(True, description="Set as default payment method")

class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Cancellation reason")
    immediate: bool = Field(False, description="Cancel immediately or at period end")

# Initialize subscription manager
subscription_manager = PlatformSubscriptionManager()


@router.get("/config")
async def get_payment_config():
    """Get UPI payment configuration for frontend"""
    try:
        config = upi_payment_service.get_upi_payment_config()
        
        return {
            "success": True,
            "data": {
                "upi": config,
                "subscription_tiers": subscription_manager.get_pricing_comparison(),
                "currency": "INR",
                "country": "IN"
            }
        }
    except Exception as e:
        logger.error(f"Error getting payment config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment configuration")


@router.post("/create-subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_verified_user)
):
    """Create a new subscription with trial period"""
    try:
        # Validate tier
        try:
            tier = SubscriptionTier(request.tier.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        # Check if user already has an active subscription
        existing_subscription = BillingSubscriptionCRUD.get_user_subscription(db, current_user.id)
        if existing_subscription:
            raise HTTPException(
                status_code=400, 
                detail="User already has an active subscription"
            )
        
        # Create subscription with UPI integration
        result = await subscription_manager.create_subscription_with_upi(
            db_session=db,
            user_id=current_user.id,
            user_email=current_user.email,
            tier=tier,
            trial_days=request.trial_days,
            user_name=f"{current_user.first_name} {current_user.last_name}".strip()
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {
            "success": True,
            "data": result["subscription"],
            "message": f"Successfully created {tier.value} subscription with {request.trial_days}-day trial"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")


@router.post("/create-payment-order")
async def create_payment_order(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create UPI payment order for subscription"""
    try:
        # Get subscription
        subscription = BillingSubscriptionCRUD.get_user_subscription(db, current_user.id)
        if not subscription or subscription.id != subscription_id:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        if subscription.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create payment order
        order_result = await upi_payment_service.create_payment_order(
            amount=subscription.monthly_price,
            customer_id=current_user.id,
            subscription_id=subscription.id,
            metadata={
                "user_id": current_user.id,
                "subscription_id": subscription.id,
                "tier": subscription.tier.value,
                "user_email": current_user.email
            }
        )
        
        if not order_result.get("success"):
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to create payment order: {order_result.get('error')}"
            )
        
        return {
            "success": True,
            "data": {
                "order": order_result["order"],
                "payment_url": order_result.get("payment_url"),
                "upi_deep_link": upi_payment_service.generate_upi_deep_link(
                    amount=subscription.monthly_price,
                    note=f"Subscription - {subscription.tier.value.title()} Plan",
                    transaction_ref=order_result["order"]["receipt"]
                )
            },
            "message": "Payment order created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment order")


@router.post("/activate-subscription")
async def activate_subscription_with_upi(
    request: UPIPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_verified_user)
):
    """Activate subscription using UPI payment verification"""
    try:
        # Get subscription
        subscription = BillingSubscriptionCRUD.get_user_subscription(db, current_user.id)
        if not subscription or subscription.id != request.subscription_id:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        if subscription.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Verify payment
        payment_result = await upi_payment_service.verify_payment(
            payment_id=request.payment_id,
            order_id=request.order_id,
            signature=request.signature
        )
        
        if not payment_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Payment verification failed: {payment_result.get('error')}"
            )
        
        # If payment verified, activate subscription
        payment_info = payment_result["payment"]
        if payment_info["status"] in ["captured", "success", "completed"]:
            # Create payment record
            payment = PaymentCRUD.create_payment(
                db=db,
                user_id=current_user.id,
                subscription_id=subscription.id,
                amount=subscription.monthly_price,
                provider=PaymentProvider.UPI,
                description=f"Subscription activation - {subscription.tier.value.title()} Plan"
            )
            
            # Update payment with success status
            PaymentCRUD.update_payment_status(
                db=db,
                payment_id=payment.id,
                status=PaymentStatus.SUCCEEDED,
                provider_payment_id=payment_info["id"]
            )
            
            # Activate subscription
            BillingSubscriptionCRUD.update_subscription_status(
                db=db,
                subscription_id=subscription.id,
                status=subscription_manager.SubscriptionStatus.ACTIVE
            )
            
            return {
                "success": True,
                "data": {
                    "subscription_id": subscription.id,
                    "payment_id": payment.id,
                    "status": "active"
                },
                "message": "Subscription activated successfully"
            }
        else:
            return {
                "success": False,
                "error": "Payment not completed",
                "payment_status": payment_info["status"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate subscription")


@router.get("/subscriptions/current")
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's current subscription details"""
    try:
        subscription = BillingSubscriptionCRUD.get_user_subscription(db, current_user.id)
        
        if not subscription:
            return {
                "success": True,
                "data": None,
                "message": "No active subscription found"
            }
        
        # Calculate usage percentages
        campaigns_percentage = (
            (subscription.campaigns_used / subscription.max_campaigns * 100) 
            if subscription.max_campaigns != -1 else 0
        )
        
        ai_percentage = (
            (subscription.ai_generations_used / subscription.max_ai_generations * 100) 
            if subscription.max_ai_generations != -1 else 0
        )
        
        api_percentage = (
            (subscription.api_calls_used / subscription.max_api_calls * 100) 
            if subscription.max_api_calls != -1 else 0
        )
        
        # Calculate days remaining in trial
        trial_days_remaining = None
        if subscription.is_trial and subscription.trial_end:
            remaining = (subscription.trial_end - datetime.utcnow()).days
            trial_days_remaining = max(0, remaining)
        
        subscription_data = {
            "subscription_id": subscription.id,
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "monthly_price": subscription.monthly_price,
            "currency": subscription.currency,
            "is_trial": subscription.is_trial,
            "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
            "trial_days_remaining": trial_days_remaining,
            "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            "limits": {
                "campaigns": subscription.max_campaigns if subscription.max_campaigns != -1 else "unlimited",
                "ai_generations": subscription.max_ai_generations if subscription.max_ai_generations != -1 else "unlimited",
                "api_calls": subscription.max_api_calls if subscription.max_api_calls != -1 else "unlimited",
                "analytics_retention_days": subscription.analytics_retention_days
            },
            "usage": {
                "campaigns": {
                    "used": subscription.campaigns_used,
                    "limit": subscription.max_campaigns if subscription.max_campaigns != -1 else "unlimited",
                    "percentage": campaigns_percentage
                },
                "ai_generations": {
                    "used": subscription.ai_generations_used,
                    "limit": subscription.max_ai_generations if subscription.max_ai_generations != -1 else "unlimited",
                    "percentage": ai_percentage
                },
                "api_calls": {
                    "used": subscription.api_calls_used,
                    "limit": subscription.max_api_calls if subscription.max_api_calls != -1 else "unlimited",
                    "percentage": api_percentage
                }
            },
            "features": subscription_manager.PRICING[subscription.tier]['features'],
            "created_at": subscription.created_at.isoformat(),
            "updated_at": subscription.updated_at.isoformat()
        }
        
        return {
            "success": True,
            "data": subscription_data
        }
        
    except Exception as e:
        logger.error(f"Error getting current subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription details")


@router.post("/subscriptions/cancel")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel user's subscription"""
    try:
        subscription = BillingSubscriptionCRUD.get_user_subscription(db, current_user.id)
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        if subscription.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Cancel Stripe subscription if exists
        if subscription.stripe_subscription_id:
            stripe_result = await google_pay_service.cancel_subscription(
                subscription.stripe_subscription_id
            )
            
            if not stripe_result.get("success"):
                logger.warning(f"Failed to cancel Stripe subscription: {stripe_result.get('error')}")
        
        # Update database subscription
        success = BillingSubscriptionCRUD.cancel_subscription(db, subscription.id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
        
        return {
            "success": True,
            "data": {
                "subscription_id": subscription.id,
                "status": "canceled",
                "canceled_at": datetime.utcnow().isoformat()
            },
            "message": "Subscription canceled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.get("/billing/history")
async def get_billing_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's payment and invoice history"""
    try:
        # Get payments
        payments = PaymentCRUD.get_user_payments(db, current_user.id, limit=limit)
        
        # Get invoices
        invoices = InvoiceCRUD.get_user_invoices(db, current_user.id, limit=limit)
        
        payment_history = []
        for payment in payments:
            payment_history.append({
                "id": payment.id,
                "type": "payment",
                "amount": payment.amount,
                "currency": payment.currency,
                "description": payment.description,
                "status": payment.status.value,
                "provider": payment.provider.value,
                "created_at": payment.created_at.isoformat(),
                "processed_at": payment.processed_at.isoformat() if payment.processed_at else None
            })
        
        for invoice in invoices:
            payment_history.append({
                "id": invoice.id,
                "type": "invoice",
                "invoice_number": invoice.invoice_number,
                "amount": invoice.total,
                "currency": invoice.currency,
                "status": invoice.status,
                "period_start": invoice.period_start.isoformat(),
                "period_end": invoice.period_end.isoformat(),
                "created_at": invoice.created_at.isoformat(),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
            })
        
        # Sort by creation date
        payment_history.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "data": payment_history[:limit],
            "total": len(payment_history)
        }
        
    except Exception as e:
        logger.error(f"Error getting billing history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing history")


@router.post("/update-payment-method")
async def update_payment_method(
    request: UpdatePaymentMethodRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user's payment method with UPI ID"""
    try:
        # Create payment method record
        payment_method = PaymentMethodCRUD.create_payment_method(
            db=db,
            user_id=current_user.id,
            provider=PaymentProvider.UPI,
            provider_method_id=f"upi_{current_user.id}_{datetime.utcnow().timestamp()}",
            method_type="upi",
            upi_details={
                "upi_id": request.upi_id,
                "gateway": upi_payment_service.gateway
            },
            is_default=request.is_default
        )
        
        return {
            "success": True,
            "data": {
                "payment_method_id": payment_method.id,
                "type": payment_method.type,
                "provider": payment_method.provider.value,
                "upi_id": request.upi_id,
                "is_default": payment_method.is_default
            },
            "message": "Payment method updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating payment method: {e}")
        raise HTTPException(status_code=500, detail="Failed to update payment method")


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payment status by order ID"""
    try:
        # Get payment by order ID (using receipt field)
        payment = db.query(Payment).filter(
            Payment.user_id == current_user.id
        ).join(BillingSubscription, Payment.subscription_id == BillingSubscription.id).filter(
            BillingSubscription.user_id == current_user.id
        ).first()
        
        if not payment:
            return {
                "success": True,
                "data": {
                    "status": "pending",
                    "order_id": order_id,
                    "payment_id": None,
                    "error_message": None
                }
            }
        
        # Map payment status to frontend expected format
        status_mapping = {
            PaymentStatus.PENDING: "pending",
            PaymentStatus.SUCCEEDED: "succeeded", 
            PaymentStatus.FAILED: "failed",
            PaymentStatus.CANCELED: "cancelled"
        }
        
        return {
            "success": True,
            "data": {
                "status": status_mapping.get(payment.status, "pending"),
                "order_id": order_id,
                "payment_id": payment.provider_payment_id,
                "error_message": payment.failure_reason
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment status")


@router.post("/webhook")
async def handle_payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle UPI payment gateway webhook events"""
    try:
        payload = await request.body()
        
        # Different gateways use different signature headers and formats
        signature_header = None
        signature_value = None
        
        # Determine signature header and extract signature
        if request.headers.get("x-razorpay-signature"):
            signature_header = "x-razorpay-signature"
            signature_value = request.headers.get("x-razorpay-signature")
        elif request.headers.get("x-cashfree-signature"):
            signature_header = "x-cashfree-signature" 
            signature_value = request.headers.get("x-cashfree-signature")
        elif request.headers.get("signature"):
            signature_header = "signature"
            signature_value = request.headers.get("signature")
        else:
            logger.warning(f"No signature header found in webhook request. Headers: {dict(request.headers)}")
            raise HTTPException(status_code=400, detail="Missing signature header")
        
        # Validate signature format
        if not signature_value or not isinstance(signature_value, str) or len(signature_value.strip()) == 0:
            logger.warning(f"Invalid signature format: {signature_value}")
            raise HTTPException(status_code=400, detail="Invalid signature format")
        
        # Verify webhook signature with enhanced validation
        verification_result = upi_payment_service.verify_webhook_signature(
            payload.decode(), 
            signature_value, 
            signature_header
        )
        
        if not verification_result:
            logger.warning(f"Webhook signature verification failed. Header: {signature_header}, Signature: {signature_value[:20]}...")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook event
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Store webhook event
        webhook_event = WebhookEventCRUD.create_webhook_event(
            db=db,
            provider=PaymentProvider.UPI,
            event_type=event_data.get("event") or event_data.get("type"),
            provider_event_id=event_data.get("payment_id") or event_data.get("id"),
            data=event_data,
            request_headers=dict(request.headers),
            request_signature=signature_value
        )
        
        # Process webhook in background
        background_tasks.add_task(process_webhook_event, webhook_event.id, event_data)
        
        return {"success": True, "message": "Webhook received"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


async def process_webhook_event(webhook_id: str, event_data: Dict[str, Any]):
    """Process webhook event in background"""
    # Create a new database session for background task
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        event_type = event_data.get("type")
        event_object = event_data.get("data", {}).get("object", {})
        
        if event_type == "payment_intent.succeeded":
            # Handle successful payment
            payment_intent_id = event_object.get("id")
            
            # Find payment record
            payment = PaymentCRUD.get_payment_by_provider_id(db, payment_intent_id)
            if payment:
                PaymentCRUD.update_payment_status(
                    db=db,
                    payment_id=payment.id,
                    status=PaymentStatus.SUCCEEDED,
                    provider_payment_id=payment_intent_id
                )
        
        elif event_type == "payment_intent.payment_failed":
            # Handle failed payment
            payment_intent_id = event_object.get("id")
            failure_code = event_object.get("last_payment_error", {}).get("code")
            failure_message = event_object.get("last_payment_error", {}).get("message")
            
            payment = PaymentCRUD.get_payment_by_provider_id(db, payment_intent_id)
            if payment:
                PaymentCRUD.update_payment_status(
                    db=db,
                    payment_id=payment.id,
                    status=PaymentStatus.FAILED,
                    failure_reason=failure_message,
                    failure_code=failure_code
                )
        
        elif event_type == "invoice.payment_succeeded":
            # Handle successful subscription payment
            invoice_id = event_object.get("id")
            subscription_id = event_object.get("subscription")
            
            # Handle recurring billing
            pass
        
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription_id = event_object.get("id")
            
            # Find and cancel subscription in database
            pass
        
        # Mark webhook as processed
        WebhookEventCRUD.mark_webhook_processed(db, webhook_id)
        
    except Exception as e:
        logger.error(f"Error processing webhook event {webhook_id}: {e}")
        WebhookEventCRUD.mark_webhook_processed(db, webhook_id, str(e))
    finally:
        db.close()