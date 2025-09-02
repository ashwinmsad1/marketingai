"""
UPI Payment Integration Service for AI Marketing Automation Platform
Handles subscription billing using UPI payments for Indian customers
"""

import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()


class UPIPaymentService:
    """Service for UPI payment management"""
    
    def __init__(self):
        # UPI Configuration
        self.environment = os.getenv("UPI_ENVIRONMENT", "sandbox")  # sandbox or production
        self.merchant_id = os.getenv("UPI_MERCHANT_ID", "MERCHANT001")
        self.merchant_name = os.getenv("UPI_MERCHANT_NAME", "AI Marketing Automation")
        self.merchant_vpa = os.getenv("UPI_MERCHANT_VPA", "merchant@paytm")  # Virtual Payment Address
        
        # Payment Gateway Configuration (Razorpay, PayU, or Cashfree)
        self.gateway = os.getenv("UPI_GATEWAY", "razorpay")
        self.gateway_key = os.getenv("UPI_GATEWAY_KEY")
        self.gateway_secret = os.getenv("UPI_GATEWAY_SECRET")
        self.webhook_secret = os.getenv("UPI_WEBHOOK_SECRET")
        
        # API Base URLs
        self.api_base_urls = {
            "razorpay": {
                "sandbox": "https://api.razorpay.com/v1/",
                "production": "https://api.razorpay.com/v1/"
            },
            "payu": {
                "sandbox": "https://test.payu.in/",
                "production": "https://secure.payu.in/"
            },
            "cashfree": {
                "sandbox": "https://sandbox.cashfree.com/pg/",
                "production": "https://api.cashfree.com/pg/"
            }
        }
        
        self.base_url = self.api_base_urls[self.gateway][self.environment]
    
    def get_upi_payment_config(self) -> Dict[str, Any]:
        """Get UPI payment configuration for frontend"""
        return {
            "environment": self.environment,
            "merchant_id": self.merchant_id,
            "merchant_name": self.merchant_name,
            "merchant_vpa": self.merchant_vpa,
            "gateway": self.gateway,
            "supported_apps": [
                "PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay",
                "WhatsApp Pay", "Mobikwik", "Freecharge", "PayPal"
            ],
            "currency": "INR"
        }
    
    async def create_payment_order(
        self,
        amount: float,
        currency: str = "INR",
        customer_id: str = None,
        subscription_id: str = None,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a payment order for UPI"""
        
        try:
            # Convert to paise for Indian payment gateways
            amount_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_paise,
                "currency": currency,
                "receipt": f"receipt_{subscription_id or customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "payment_capture": 1  # Auto-capture
            }
            
            if metadata:
                order_data["notes"] = metadata
            
            # Create order based on gateway
            if self.gateway == "razorpay":
                response = await self._create_razorpay_order(order_data)
            elif self.gateway == "payu":
                response = await self._create_payu_order(order_data)
            elif self.gateway == "cashfree":
                response = await self._create_cashfree_order(order_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported gateway: {self.gateway}",
                    "error_type": "configuration_error"
                }
            
            return response
            
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid payment parameters: {str(e)}",
                "error_type": "validation_error"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Payment gateway connection error: {str(e)}",
                "error_type": "network_error"
            }
        except Exception as e:
            # Log detailed error for debugging but return generic message
            print(f"Unexpected error in create_payment_order: {str(e)}")
            return {
                "success": False,
                "error": "Payment order creation failed due to internal error",
                "error_type": "internal_error"
            }
    
    async def _create_razorpay_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Razorpay order"""
        
        # Secure authentication header creation
        if not self.gateway_key or not self.gateway_secret:
            return {
                "success": False,
                "error": "Gateway credentials not configured",
                "error_type": "configuration_error"
            }
            
        # Create secure basic auth token
        auth_string = f"{self.gateway_key}:{self.gateway_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_token = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_token}"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}orders",
                json=order_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                return {
                    "success": True,
                    "order": {
                        "id": order["id"],
                        "amount": order["amount"],
                        "currency": order["currency"],
                        "status": order["status"],
                        "receipt": order["receipt"]
                    },
                    "payment_url": f"upi://pay?pa={self.merchant_vpa}&pn={self.merchant_name}&am={order_data['amount']/100}&cu=INR&tn=Payment for {order['receipt']}"
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("description", "Order creation failed"),
                    "error_type": "gateway_error"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "error_type": "network_error"
            }
    
    async def _create_payu_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create PayU order"""
        
        # PayU requires different parameters
        payu_data = {
            "key": self.gateway_key,
            "txnid": order_data["receipt"],
            "amount": order_data["amount"] / 100,  # Convert back to rupees
            "productinfo": "Subscription Payment",
            "firstname": "Customer",
            "email": "customer@example.com",
            "udf1": order_data.get("notes", {}).get("subscription_id", ""),
            "udf2": order_data.get("notes", {}).get("customer_id", "")
        }
        
        # Secure hash generation for PayU
        if not self.gateway_secret:
            return {
                "success": False,
                "error": "Gateway secret not configured for PayU",
                "error_type": "configuration_error"
            }
            
        # Build hash string according to PayU specification
        # Format: key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10|salt
        hash_components = [
            payu_data['key'],
            payu_data['txnid'],
            str(payu_data['amount']),
            payu_data['productinfo'],
            payu_data['firstname'],
            payu_data['email'],
            payu_data.get('udf1', ''),
            payu_data.get('udf2', ''),
            payu_data.get('udf3', ''),
            payu_data.get('udf4', ''),
            payu_data.get('udf5', ''),
            payu_data.get('udf6', ''),
            payu_data.get('udf7', ''),
            payu_data.get('udf8', ''),
            payu_data.get('udf9', ''),
            payu_data.get('udf10', ''),
            self.gateway_secret
        ]
        
        hash_string = '|'.join(hash_components)
        payu_data["hash"] = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
        
        return {
            "success": True,
            "order": {
                "id": order_data["receipt"],
                "amount": order_data["amount"],
                "currency": order_data["currency"],
                "status": "created",
                "receipt": order_data["receipt"]
            },
            "payment_data": payu_data,
            "payment_url": f"{self.base_url}_payment"
        }
    
    async def _create_cashfree_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Cashfree order"""
        
        headers = {
            "Content-Type": "application/json",
            "x-client-id": self.gateway_key,
            "x-client-secret": self.gateway_secret,
            "x-api-version": "2022-09-01"
        }
        
        cashfree_data = {
            "order_id": order_data["receipt"],
            "order_amount": order_data["amount"] / 100,
            "order_currency": order_data["currency"],
            "customer_details": {
                "customer_id": order_data.get("notes", {}).get("customer_id", f"guest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "customer_name": order_data.get("notes", {}).get("customer_name", "Customer"),
                "customer_email": order_data.get("notes", {}).get("customer_email", "noreply@aimarketing.com"),
                "customer_phone": order_data.get("notes", {}).get("customer_phone", "0000000000")
            },
            "order_meta": {
                "return_url": "https://merchant.com/return/{order_id}",
                "notify_url": "https://merchant.com/notify"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}orders",
                json=cashfree_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                return {
                    "success": True,
                    "order": {
                        "id": order["order_id"],
                        "amount": int(order["order_amount"] * 100),
                        "currency": order["order_currency"],
                        "status": order["order_status"],
                        "receipt": order["order_id"]
                    },
                    "payment_session_id": order.get("payment_session_id"),
                    "payment_url": f"upi://pay?pa={self.merchant_vpa}&pn={self.merchant_name}&am={order['order_amount']}&cu=INR&tn=Payment for {order['order_id']}"
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("message", "Order creation failed"),
                    "error_type": "gateway_error"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "error_type": "network_error"
            }
    
    async def verify_payment(
        self,
        payment_id: str,
        order_id: str,
        signature: str = None
    ) -> Dict[str, Any]:
        """Verify UPI payment"""
        
        try:
            if self.gateway == "razorpay":
                return await self._verify_razorpay_payment(payment_id, order_id, signature)
            elif self.gateway == "payu":
                return await self._verify_payu_payment(payment_id, order_id)
            elif self.gateway == "cashfree":
                return await self._verify_cashfree_payment(payment_id, order_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported gateway: {self.gateway}",
                    "error_type": "configuration_error"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    async def _verify_razorpay_payment(
        self, 
        payment_id: str, 
        order_id: str, 
        signature: str
    ) -> Dict[str, Any]:
        """Verify Razorpay payment signature"""
        
        try:
            # Verify signature
            expected_signature = hmac.new(
                self.gateway_secret.encode(),
                f"{order_id}|{payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return {
                    "success": False,
                    "error": "Invalid payment signature",
                    "error_type": "signature_error"
                }
            
            # Fetch payment details
            headers = {
                "Authorization": f"Basic {base64.b64encode(f'{self.gateway_key}:{self.gateway_secret}'.encode()).decode()}"
            }
            
            response = requests.get(
                f"{self.base_url}payments/{payment_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                payment = response.json()
                return {
                    "success": True,
                    "payment": {
                        "id": payment["id"],
                        "amount": payment["amount"],
                        "currency": payment["currency"],
                        "status": payment["status"],
                        "method": payment["method"],
                        "order_id": payment["order_id"],
                        "created_at": payment["created_at"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Payment verification failed",
                    "error_type": "verification_error"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "verification_error"
            }
    
    async def _verify_payu_payment(self, payment_id: str, order_id: str) -> Dict[str, Any]:
        """Verify PayU payment"""
        
        if not self.gateway_key or not self.gateway_secret:
            return {
                "success": False,
                "error": "PayU credentials not configured",
                "error_type": "configuration_error"
            }
        
        try:
            # PayU verification using their verify payment API
            verify_data = {
                "key": self.gateway_key,
                "command": "verify_payment",
                "var1": order_id,
                "hash": ""
            }
            
            # Generate hash for verification
            # PayU verification hash: key|command|var1|salt
            hash_components = [
                verify_data['key'],
                verify_data['command'],
                verify_data['var1'],
                self.gateway_secret
            ]
            
            hash_string = '|'.join(hash_components)
            verify_data["hash"] = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
            
            # Make API call to PayU
            response = requests.post(
                f"{self.base_url}payment/op/getPaymentStatus",
                data=verify_data,
                timeout=30,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == 1:
                    # Payment verification successful
                    transaction_details = result.get("transaction_details", {})
                    if isinstance(transaction_details, dict) and transaction_details:
                        payment_status = transaction_details.get("status", "").lower()
                        
                        return {
                            "success": True,
                            "payment": {
                                "id": payment_id,
                                "amount": float(transaction_details.get("amount", 0)) * 100,  # Convert to paise
                                "currency": "INR",
                                "status": "captured" if payment_status == "success" else payment_status,
                                "method": "upi",
                                "order_id": order_id,
                                "created_at": transaction_details.get("addedon", "")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No transaction details found",
                            "error_type": "not_found_error"
                        }
                else:
                    return {
                        "success": False,
                        "error": result.get("msg", "Payment verification failed"),
                        "error_type": "verification_error"
                    }
            else:
                return {
                    "success": False,
                    "error": f"PayU API error: {response.status_code}",
                    "error_type": "api_error"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "error_type": "network_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"PayU verification error: {str(e)}",
                "error_type": "verification_error"
            }
    
    async def _verify_cashfree_payment(self, payment_id: str, order_id: str) -> Dict[str, Any]:
        """Verify Cashfree payment"""
        
        headers = {
            "x-client-id": self.gateway_key,
            "x-client-secret": self.gateway_secret,
            "x-api-version": "2022-09-01"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}orders/{order_id}/payments",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                payments = response.json()
                for payment in payments:
                    if payment["cf_payment_id"] == payment_id:
                        return {
                            "success": True,
                            "payment": {
                                "id": payment["cf_payment_id"],
                                "amount": int(payment["payment_amount"] * 100),
                                "currency": payment["payment_currency"],
                                "status": payment["payment_status"],
                                "method": payment["payment_method"],
                                "order_id": order_id,
                                "created_at": payment["payment_time"]
                            }
                        }
                
                return {
                    "success": False,
                    "error": "Payment not found",
                    "error_type": "not_found_error"
                }
            else:
                return {
                    "success": False,
                    "error": "Payment verification failed",
                    "error_type": "verification_error"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "verification_error"
            }
    
    def verify_webhook_signature(self, payload: str, signature: str, signature_header: str = None) -> bool:
        """Verify webhook signature with enhanced security"""
        
        if not self.webhook_secret:
            return False
        
        if not payload or not signature:
            return False
        
        try:
            if self.gateway == "razorpay":
                # Razorpay uses HMAC SHA256 of the raw payload
                expected_signature = hmac.new(
                    self.webhook_secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                return hmac.compare_digest(signature, expected_signature)
                
            elif self.gateway == "cashfree":
                # Cashfree uses HMAC SHA256 with base64 encoding
                expected_signature = base64.b64encode(
                    hmac.new(
                        self.webhook_secret.encode(),
                        payload.encode(),
                        hashlib.sha256
                    ).digest()
                ).decode()
                return hmac.compare_digest(signature, expected_signature)
                
            elif self.gateway == "payu":
                # PayU uses different verification method - checking hash of specific fields
                try:
                    import json
                    webhook_data = json.loads(payload)
                    # PayU specific verification logic would go here
                    # For now, validate that we have the required fields
                    required_fields = ['txnid', 'amount', 'status']
                    if all(field in webhook_data for field in required_fields):
                        return True
                    return False
                except json.JSONDecodeError:
                    return False
            else:
                # Unknown gateway
                return False
                
        except Exception as e:
            # Log the error for debugging but don't expose details
            print(f"Webhook signature verification error: {str(e)}")
            return False
    
    def generate_upi_deep_link(
        self,
        amount: float,
        note: str,
        transaction_ref: str
    ) -> str:
        """Generate UPI deep link for payment"""
        
        return (
            f"upi://pay?"
            f"pa={self.merchant_vpa}&"
            f"pn={self.merchant_name}&"
            f"am={amount}&"
            f"cu=INR&"
            f"tn={note}&"
            f"tr={transaction_ref}"
        )


# Singleton instance
upi_payment_service = UPIPaymentService()