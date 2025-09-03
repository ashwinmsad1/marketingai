"""
CRUD operations for Google Pay and payment processing
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .models import (
    BillingSubscription, Payment, Invoice, PaymentMethod, WebhookEvent,
    User, SubscriptionTier, SubscriptionStatus, PaymentStatus, PaymentProvider
)
import uuid


class BillingSubscriptionCRUD:
    """CRUD operations for billing subscriptions"""
    
    @staticmethod
    def get_user_active_subscription(db: Session, user_id: str) -> Optional[BillingSubscription]:
        """Get user's active subscription"""
        return db.query(BillingSubscription).filter(
            BillingSubscription.user_id == user_id,
            BillingSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    @staticmethod
    def create_subscription(
        db: Session, 
        user_id: str, 
        tier: SubscriptionTier,
        monthly_price: float,
        trial_days: int = 14,
        provider: PaymentProvider = PaymentProvider.GOOGLE_PAY
    ) -> BillingSubscription:
        """Create a new billing subscription"""
        
        # Calculate trial period
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=trial_days)
        
        # Set subscription limits based on tier - Updated for simplified business plans
        limits = {
            SubscriptionTier.STARTER: {  # Essential Plan
                'max_campaigns': 10,
                'max_ai_generations': -1,  # Unlimited basic AI content
                'max_api_calls': 2000,
                'analytics_retention_days': 30
            },
            SubscriptionTier.PROFESSIONAL: {  # Growth Plan
                'max_campaigns': 50,
                'max_ai_generations': -1,  # Unlimited advanced AI content
                'max_api_calls': 10000,
                'analytics_retention_days': 90
            },
            SubscriptionTier.ENTERPRISE: {  # Professional Plan
                'max_campaigns': -1,  # Unlimited
                'max_ai_generations': -1,  # Unlimited premium AI content
                'max_api_calls': -1,
                'analytics_retention_days': 365
            }
        }
        
        tier_limits = limits.get(tier, limits[SubscriptionTier.STARTER])
        
        subscription = BillingSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tier=tier,
            status=SubscriptionStatus.TRIAL,
            monthly_price=monthly_price,
            trial_start=trial_start,
            trial_end=trial_end,
            is_trial=True,
            billing_cycle_start=trial_end,
            next_billing_date=trial_end,
            provider=provider,
            **tier_limits
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def get_user_subscription(db: Session, user_id: str) -> Optional[BillingSubscription]:
        """Get user's active subscription"""
        return db.query(BillingSubscription).filter(
            BillingSubscription.user_id == user_id,
            BillingSubscription.status.in_([
                SubscriptionStatus.ACTIVE, 
                SubscriptionStatus.TRIAL,
                SubscriptionStatus.PAST_DUE
            ])
        ).order_by(desc(BillingSubscription.created_at)).first()
    
    @staticmethod
    def update_subscription_status(
        db: Session, 
        subscription_id: str, 
        status: SubscriptionStatus,
        provider_subscription_id: str = None
    ) -> Optional[BillingSubscription]:
        """Update subscription status"""
        subscription = db.query(BillingSubscription).filter(
            BillingSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        subscription.status = status
        subscription.updated_at = datetime.utcnow()
        
        if provider_subscription_id:
            subscription.provider_subscription_id = provider_subscription_id
        
        # If activating from trial, update billing dates with idempotency check
        if status == SubscriptionStatus.ACTIVE and subscription.is_trial:
            # Check if this subscription has already been activated to prevent double-processing
            if subscription.status == SubscriptionStatus.ACTIVE:
                # Already activated, skip to prevent duplicate processing
                return subscription
                
            subscription.is_trial = False
            subscription.billing_cycle_start = datetime.utcnow()
            subscription.next_billing_date = datetime.utcnow() + timedelta(days=30)
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def cancel_subscription(db: Session, subscription_id: str) -> bool:
        """Cancel a subscription"""
        subscription = db.query(BillingSubscription).filter(
            BillingSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    def track_usage(
        db: Session, 
        subscription_id: str, 
        usage_type: str, 
        amount: int = 1
    ) -> Optional[BillingSubscription]:
        """Track usage for subscription"""
        subscription = db.query(BillingSubscription).filter(
            BillingSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        if usage_type == 'campaigns':
            subscription.campaigns_used += amount
        elif usage_type == 'ai_generations':
            subscription.ai_generations_used += amount
        elif usage_type == 'api_calls':
            subscription.api_calls_used += amount
        
        subscription.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def check_usage_limits(subscription: BillingSubscription, usage_type: str) -> tuple[bool, str]:
        """Check if user has reached usage limits"""
        if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
            return False, f"Subscription is {subscription.status.value}"
        
        if usage_type == 'campaigns':
            if subscription.max_campaigns == -1:  # Unlimited
                return True, ""
            if subscription.campaigns_used >= subscription.max_campaigns:
                return False, f"Campaign limit reached ({subscription.max_campaigns})"
        
        elif usage_type == 'ai_generations':
            if subscription.max_ai_generations == -1:
                return True, ""
            if subscription.ai_generations_used >= subscription.max_ai_generations:
                return False, f"AI generation limit reached ({subscription.max_ai_generations})"
        
        elif usage_type == 'api_calls':
            if subscription.max_api_calls == -1:
                return True, ""
            if subscription.api_calls_used >= subscription.max_api_calls:
                return False, f"API call limit reached ({subscription.max_api_calls})"
        
        return True, ""


class PaymentCRUD:
    """CRUD operations for payments"""
    
    @staticmethod
    def create_payment(
        db: Session,
        user_id: str,
        subscription_id: str,
        amount: float,
        provider: PaymentProvider,
        description: str = "Monthly subscription",
        currency: str = "INR"
    ) -> Payment:
        """Create a new payment record"""
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            description=description,
            provider=provider,
            status=PaymentStatus.PENDING
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def update_payment_status(
        db: Session,
        payment_id: str,
        status: PaymentStatus,
        provider_payment_id: str = None,
        provider_transaction_id: str = None,
        failure_reason: str = None,
        failure_code: str = None
    ) -> Optional[Payment]:
        """Update payment status"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return None
        
        payment.status = status
        payment.updated_at = datetime.utcnow()
        
        if provider_payment_id:
            payment.provider_payment_id = provider_payment_id
        
        if provider_transaction_id:
            payment.provider_transaction_id = provider_transaction_id
        
        if failure_reason:
            payment.failure_reason = failure_reason
            
        if failure_code:
            payment.failure_code = failure_code
        
        if status == PaymentStatus.SUCCEEDED:
            payment.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def get_user_payments(
        db: Session, 
        user_id: str, 
        limit: int = 50,
        status: PaymentStatus = None
    ) -> List[Payment]:
        """Get user's payment history"""
        query = db.query(Payment).filter(Payment.user_id == user_id)
        
        if status:
            query = query.filter(Payment.status == status)
        
        return query.order_by(desc(Payment.created_at)).limit(limit).all()
    
    @staticmethod
    def get_payment_by_provider_id(
        db: Session, 
        provider_payment_id: str
    ) -> Optional[Payment]:
        """Get payment by provider's payment ID"""
        return db.query(Payment).filter(
            Payment.provider_payment_id == provider_payment_id
        ).first()


class InvoiceCRUD:
    """CRUD operations for invoices"""
    
    @staticmethod
    def create_invoice(
        db: Session,
        user_id: str,
        subscription_id: str,
        amount: float,
        period_start: datetime,
        period_end: datetime,
        line_items: List[Dict[str, Any]],
        currency: str = "INR"
    ) -> Invoice:
        """Create a new invoice"""
        # Generate invoice number
        invoice_count = db.query(Invoice).count() + 1
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{invoice_count:04d}"
        
        invoice = Invoice(
            id=str(uuid.uuid4()),
            user_id=user_id,
            subscription_id=subscription_id,
            invoice_number=invoice_number,
            amount=amount,
            currency=currency,
            period_start=period_start,
            period_end=period_end,
            line_items=line_items,
            subtotal=amount,
            total=amount,
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def get_user_invoices(
        db: Session, 
        user_id: str, 
        limit: int = 50
    ) -> List[Invoice]:
        """Get user's invoices"""
        return db.query(Invoice).filter(
            Invoice.user_id == user_id
        ).order_by(desc(Invoice.created_at)).limit(limit).all()
    
    @staticmethod
    def mark_invoice_paid(
        db: Session, 
        invoice_id: str, 
        payment_id: str
    ) -> Optional[Invoice]:
        """Mark invoice as paid"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            return None
        
        invoice.status = "paid"
        invoice.payment_id = payment_id
        invoice.paid_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(invoice)
        
        return invoice


class PaymentMethodCRUD:
    """CRUD operations for payment methods"""
    
    @staticmethod
    def create_payment_method(
        db: Session,
        user_id: str,
        provider: PaymentProvider,
        provider_method_id: str,
        method_type: str,
        card_details: Dict[str, Any] = None,
        google_pay_details: Dict[str, Any] = None,
        upi_details: Dict[str, Any] = None,
        is_default: bool = False
    ) -> PaymentMethod:
        """Create a new payment method"""
        
        # If this is the default, unset other defaults atomically
        if is_default:
            try:
                # Begin transaction to prevent race conditions
                db.begin()
                
                # Lock existing payment methods for this user to prevent race conditions
                existing_defaults = db.query(PaymentMethod).filter(
                    PaymentMethod.user_id == user_id,
                    PaymentMethod.is_default == True,
                    PaymentMethod.is_active == True
                ).with_for_update().all()
                
                # Unset all existing defaults
                for payment_method in existing_defaults:
                    payment_method.is_default = False
                    db.add(payment_method)
                    
            except Exception as e:
                db.rollback()
                raise Exception(f"Failed to update default payment method: {str(e)}")
        
        payment_method = PaymentMethod(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            provider_method_id=provider_method_id,
            type=method_type,
            is_default=is_default
        )
        
        # Add card details if provided
        if card_details:
            payment_method.card_last4 = card_details.get('last4')
            payment_method.card_brand = card_details.get('brand')
            payment_method.card_exp_month = card_details.get('exp_month')
            payment_method.card_exp_year = card_details.get('exp_year')
        
        # Add Google Pay details if provided
        if google_pay_details:
            payment_method.google_pay_merchant_id = google_pay_details.get('merchant_id')
            payment_method.google_pay_gateway = google_pay_details.get('gateway')
        
        # Add UPI details if provided (stored as JSON in metadata or similar field)
        if upi_details:
            # Store UPI details securely - this would need a metadata field or similar
            # For now, we'll use the existing structure
            pass
        
        try:
            db.add(payment_method)
            db.commit()
            db.refresh(payment_method)
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create payment method: {str(e)}")
        
        return payment_method
    
    @staticmethod
    def get_user_payment_methods(db: Session, user_id: str) -> List[PaymentMethod]:
        """Get user's payment methods"""
        return db.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id,
            PaymentMethod.is_active == True
        ).order_by(desc(PaymentMethod.is_default), desc(PaymentMethod.created_at)).all()
    
    @staticmethod
    def set_default_payment_method(
        db: Session, 
        user_id: str, 
        payment_method_id: str
    ) -> bool:
        """Set a payment method as default"""
        # Unset current default
        db.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id,
            PaymentMethod.is_default == True
        ).update({'is_default': False})
        
        # Set new default
        result = db.query(PaymentMethod).filter(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.user_id == user_id
        ).update({'is_default': True})
        
        db.commit()
        return result > 0
    
    @staticmethod
    def delete_payment_method(db: Session, payment_method_id: str, user_id: str) -> bool:
        """Delete a payment method"""
        result = db.query(PaymentMethod).filter(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.user_id == user_id
        ).update({'is_active': False})
        
        db.commit()
        return result > 0


class WebhookEventCRUD:
    """CRUD operations for webhook events"""
    
    @staticmethod
    def create_webhook_event(
        db: Session,
        provider: PaymentProvider,
        event_type: str,
        provider_event_id: str,
        data: Dict[str, Any],
        request_headers: Dict[str, str] = None,
        request_signature: str = None
    ) -> WebhookEvent:
        """Create a new webhook event"""
        webhook_event = WebhookEvent(
            id=str(uuid.uuid4()),
            provider=provider,
            event_type=event_type,
            provider_event_id=provider_event_id,
            data=data,
            request_headers=request_headers,
            request_signature=request_signature
        )
        
        db.add(webhook_event)
        db.commit()
        db.refresh(webhook_event)
        
        return webhook_event
    
    @staticmethod
    def mark_webhook_processed(
        db: Session, 
        webhook_id: str, 
        error_message: str = None
    ) -> Optional[WebhookEvent]:
        """Mark webhook as processed"""
        webhook = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_id).first()
        
        if not webhook:
            return None
        
        webhook.processed = True
        webhook.processed_at = datetime.utcnow()
        
        if error_message:
            webhook.error_message = error_message
        
        db.commit()
        db.refresh(webhook)
        
        return webhook
    
    @staticmethod
    def get_unprocessed_webhooks(
        db: Session, 
        provider: PaymentProvider = None,
        limit: int = 100
    ) -> List[WebhookEvent]:
        """Get unprocessed webhook events"""
        query = db.query(WebhookEvent).filter(WebhookEvent.processed == False)
        
        if provider:
            query = query.filter(WebhookEvent.provider == provider)
        
        return query.order_by(WebhookEvent.created_at).limit(limit).all()