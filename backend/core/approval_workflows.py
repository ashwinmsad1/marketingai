"""
AI Decision Approval Workflows
Human oversight and approval gates for high-risk AI decisions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"

class ApprovalLevel(Enum):
    """Approval authority levels"""
    USER = "user"           # User self-approval
    MANAGER = "manager"     # Manager approval
    ADMIN = "admin"         # Admin approval
    MULTI_ADMIN = "multi_admin"  # Multiple admin approval

class DecisionType(Enum):
    """Types of AI decisions requiring approval"""
    CAMPAIGN_PREDICTION = "campaign_prediction"
    BUDGET_INCREASE = "budget_increase"
    AUDIENCE_EXPANSION = "audience_expansion"
    STRATEGY_CHANGE = "strategy_change"
    HIGH_RISK_CAMPAIGN = "high_risk_campaign"
    EMERGENCY_ACTION = "emergency_action"

@dataclass
class ApprovalRequirement:
    """Approval requirement configuration"""
    decision_type: DecisionType
    required_level: ApprovalLevel
    timeout_hours: int = 24
    escalation_hours: int = 8
    auto_reject_on_timeout: bool = False
    bypass_conditions: List[str] = field(default_factory=list)

@dataclass
class ApprovalRequest:
    """Individual approval request"""
    request_id: str
    user_id: str
    decision_type: DecisionType
    decision_data: Dict[str, Any]
    required_level: ApprovalLevel
    reason: str
    risk_assessment: Dict[str, Any]
    
    # Status tracking
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Approval tracking
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    rejections: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    context: Dict[str, Any] = field(default_factory=dict)
    urgency: str = "normal"  # low, normal, high, critical

class AIDecisionApprovalWorkflow:
    """
    AI Decision Approval Workflow System
    Manages human oversight and approval gates for AI decisions
    """
    
    def __init__(self):
        """Initialize approval workflow system"""
        
        # Configure approval requirements
        self.approval_requirements = {
            DecisionType.CAMPAIGN_PREDICTION: ApprovalRequirement(
                decision_type=DecisionType.CAMPAIGN_PREDICTION,
                required_level=ApprovalLevel.USER,
                timeout_hours=4,
                escalation_hours=2,
                bypass_conditions=["high_confidence", "low_budget"]
            ),
            DecisionType.BUDGET_INCREASE: ApprovalRequirement(
                decision_type=DecisionType.BUDGET_INCREASE,
                required_level=ApprovalLevel.MANAGER,
                timeout_hours=8,
                escalation_hours=4,
                bypass_conditions=["small_increase"]
            ),
            DecisionType.HIGH_RISK_CAMPAIGN: ApprovalRequirement(
                decision_type=DecisionType.HIGH_RISK_CAMPAIGN,
                required_level=ApprovalLevel.ADMIN,
                timeout_hours=24,
                escalation_hours=8,
                auto_reject_on_timeout=True
            ),
            DecisionType.EMERGENCY_ACTION: ApprovalRequirement(
                decision_type=DecisionType.EMERGENCY_ACTION,
                required_level=ApprovalLevel.MULTI_ADMIN,
                timeout_hours=2,
                escalation_hours=1,
                bypass_conditions=["critical_safety_issue"]
            )
        }
        
        # Active requests tracking
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.request_history: List[ApprovalRequest] = []
        
        # Configuration
        self.max_pending_per_user = 10
        self.history_retention_days = 90
        
        # Notification callbacks (to be set by application)
        self.notification_callbacks: Dict[str, Callable] = {}
    
    async def request_approval(
        self,
        user_id: str,
        decision_type: DecisionType,
        decision_data: Dict[str, Any],
        reason: str,
        risk_assessment: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        urgency: str = "normal"
    ) -> ApprovalRequest:
        """
        Create approval request for AI decision
        """
        try:
            logger.info(f"Creating approval request: {decision_type.value} for user {user_id}")
            
            # Check if approval can be bypassed
            if await self._can_bypass_approval(user_id, decision_type, decision_data, risk_assessment):
                logger.info(f"Approval bypassed for {decision_type.value} - conditions met")
                return await self._create_auto_approved_request(
                    user_id, decision_type, decision_data, "Auto-approved based on bypass conditions"
                )
            
            # Get approval requirements
            requirement = self.approval_requirements.get(decision_type)
            if not requirement:
                raise ValueError(f"No approval requirement configured for {decision_type.value}")
            
            # Check user's pending request limit
            user_pending = len([
                req for req in self.pending_requests.values()
                if req.user_id == user_id and req.status == ApprovalStatus.PENDING
            ])
            
            if user_pending >= self.max_pending_per_user:
                raise ValueError(f"User has too many pending requests: {user_pending}")
            
            # Generate request ID
            request_id = f"{user_id}_{decision_type.value}_{int(datetime.now().timestamp())}"
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(hours=requirement.timeout_hours)
            
            # Create approval request
            approval_request = ApprovalRequest(
                request_id=request_id,
                user_id=user_id,
                decision_type=decision_type,
                decision_data=decision_data,
                required_level=requirement.required_level,
                reason=reason,
                risk_assessment=risk_assessment or {},
                expires_at=expires_at,
                context=context or {},
                urgency=urgency
            )
            
            # Store request
            self.pending_requests[request_id] = approval_request
            
            # Send notifications to approvers
            await self._notify_approvers(approval_request)
            
            logger.info(f"Approval request created: {request_id} (expires: {expires_at})")
            return approval_request
            
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            # Create emergency fallback request
            return await self._create_emergency_request(
                user_id, decision_type, decision_data, str(e)
            )
    
    async def submit_approval(
        self,
        request_id: str,
        approver_id: str,
        approved: bool,
        comments: str = "",
        approver_role: str = "user"
    ) -> Dict[str, Any]:
        """Submit approval decision"""
        try:
            if request_id not in self.pending_requests:
                return {"error": "Approval request not found", "success": False}
            
            request = self.pending_requests[request_id]
            
            # Check if request is still pending
            if request.status != ApprovalStatus.PENDING:
                return {
                    "error": f"Request is no longer pending (status: {request.status.value})",
                    "success": False
                }
            
            # Check if request has expired
            if request.expires_at and datetime.now() > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                return {"error": "Approval request has expired", "success": False}
            
            # Verify approver authority
            if not self._has_approval_authority(approver_id, approver_role, request.required_level):
                return {
                    "error": "Insufficient approval authority", 
                    "success": False
                }
            
            # Record approval/rejection
            decision_record = {
                "approver_id": approver_id,
                "approver_role": approver_role,
                "timestamp": datetime.now(),
                "comments": comments
            }
            
            if approved:
                request.approvals.append(decision_record)
                logger.info(f"Approval received for {request_id} from {approver_id}")
            else:
                request.rejections.append(decision_record)
                logger.info(f"Rejection received for {request_id} from {approver_id}")
            
            # Check if sufficient approvals received
            approval_result = self._evaluate_approval_status(request)
            
            if approval_result["final"]:
                request.status = ApprovalStatus.APPROVED if approval_result["approved"] else ApprovalStatus.REJECTED
                
                # Move to history
                self.request_history.append(request)
                del self.pending_requests[request_id]
                
                logger.info(f"Approval request {request_id} finalized: {request.status.value}")
            
            return {
                "success": True,
                "request_status": request.status.value,
                "final": approval_result.get("final", False),
                "approved": approval_result.get("approved", False),
                "message": approval_result.get("message", "Decision recorded")
            }
            
        except Exception as e:
            logger.error(f"Error processing approval submission: {e}")
            return {"error": str(e), "success": False}
    
    def _has_approval_authority(
        self,
        approver_id: str,
        approver_role: str,
        required_level: ApprovalLevel
    ) -> bool:
        """Check if approver has authority for required approval level"""
        
        # Role-based authority mapping
        role_authority = {
            "user": [ApprovalLevel.USER],
            "manager": [ApprovalLevel.USER, ApprovalLevel.MANAGER],
            "admin": [ApprovalLevel.USER, ApprovalLevel.MANAGER, ApprovalLevel.ADMIN],
            "super_admin": [ApprovalLevel.USER, ApprovalLevel.MANAGER, ApprovalLevel.ADMIN, ApprovalLevel.MULTI_ADMIN]
        }
        
        allowed_levels = role_authority.get(approver_role, [])
        return required_level in allowed_levels
    
    def _evaluate_approval_status(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Evaluate if request has sufficient approvals"""
        
        try:
            # If any rejection, request is rejected
            if request.rejections:
                return {
                    "final": True,
                    "approved": False,
                    "message": "Request rejected"
                }
            
            # Check approval requirements based on level
            if request.required_level == ApprovalLevel.MULTI_ADMIN:
                # Need at least 2 admin approvals
                admin_approvals = [
                    approval for approval in request.approvals
                    if approval.get("approver_role") in ["admin", "super_admin"]
                ]
                
                if len(admin_approvals) >= 2:
                    return {
                        "final": True,
                        "approved": True,
                        "message": "Multi-admin approval achieved"
                    }
            else:
                # Single approval sufficient
                if request.approvals:
                    return {
                        "final": True,
                        "approved": True,
                        "message": "Approval received"
                    }
            
            # Not yet final
            return {
                "final": False,
                "approved": False,
                "message": "Awaiting approval"
            }
            
        except Exception as e:
            logger.error(f"Error evaluating approval status: {e}")
            return {
                "final": True,
                "approved": False,
                "message": f"Evaluation error: {e}"
            }
    
    async def _can_bypass_approval(
        self,
        user_id: str,
        decision_type: DecisionType,
        decision_data: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if approval can be bypassed based on conditions"""
        
        try:
            requirement = self.approval_requirements.get(decision_type)
            if not requirement or not requirement.bypass_conditions:
                return False
            
            for condition in requirement.bypass_conditions:
                if condition == "high_confidence":
                    confidence = decision_data.get("confidence_score", 0)
                    if confidence >= 0.9:
                        return True
                
                elif condition == "low_budget":
                    budget = decision_data.get("budget", float('inf'))
                    if budget <= 1000:
                        return True
                
                elif condition == "small_increase":
                    increase = decision_data.get("increase_percentage", 1.0)
                    if increase <= 0.1:  # 10% or less increase
                        return True
                
                elif condition == "critical_safety_issue":
                    if risk_assessment and risk_assessment.get("risk_level") == "critical":
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking bypass conditions: {e}")
            return False
    
    async def _create_auto_approved_request(
        self,
        user_id: str,
        decision_type: DecisionType,
        decision_data: Dict[str, Any],
        reason: str
    ) -> ApprovalRequest:
        """Create auto-approved request for bypass cases"""
        
        request_id = f"{user_id}_{decision_type.value}_{int(datetime.now().timestamp())}_auto"
        
        request = ApprovalRequest(
            request_id=request_id,
            user_id=user_id,
            decision_type=decision_type,
            decision_data=decision_data,
            required_level=ApprovalLevel.USER,
            reason=reason,
            risk_assessment={},
            status=ApprovalStatus.APPROVED,
            context={"auto_approved": True}
        )
        
        # Add auto-approval record
        request.approvals.append({
            "approver_id": "system",
            "approver_role": "system",
            "timestamp": datetime.now(),
            "comments": "Auto-approved based on bypass conditions"
        })
        
        # Add to history
        self.request_history.append(request)
        
        return request
    
    async def _create_emergency_request(
        self,
        user_id: str,
        decision_type: DecisionType,
        decision_data: Dict[str, Any],
        error: str
    ) -> ApprovalRequest:
        """Create emergency request when normal flow fails"""
        
        request_id = f"{user_id}_{decision_type.value}_{int(datetime.now().timestamp())}_emergency"
        
        request = ApprovalRequest(
            request_id=request_id,
            user_id=user_id,
            decision_type=DecisionType.EMERGENCY_ACTION,
            decision_data=decision_data,
            required_level=ApprovalLevel.MULTI_ADMIN,
            reason=f"Emergency approval needed due to system error: {error}",
            risk_assessment={"risk_level": "critical"},
            expires_at=datetime.now() + timedelta(hours=1),
            urgency="critical",
            context={"emergency": True, "original_error": error}
        )
        
        self.pending_requests[request_id] = request
        await self._notify_approvers(request, emergency=True)
        
        return request
    
    async def _notify_approvers(self, request: ApprovalRequest, escalated: bool = False, emergency: bool = False):
        """Send notifications to appropriate approvers"""
        
        try:
            # In production, this would integrate with notification systems
            message_type = "EMERGENCY" if emergency else ("ESCALATED" if escalated else "NEW")
            
            notification_message = (
                f"🔔 {message_type} Approval Request\n"
                f"ID: {request.request_id}\n"
                f"Type: {request.decision_type.value}\n"
                f"User: {request.user_id}\n"
                f"Reason: {request.reason}\n"
                f"Urgency: {request.urgency}\n"
                f"Required Level: {request.required_level.value}\n"
                f"Expires: {request.expires_at.strftime('%Y-%m-%d %H:%M') if request.expires_at else 'N/A'}"
            )
            
            logger.info(f"APPROVAL NOTIFICATION: {notification_message}")
            
        except Exception as e:
            logger.error(f"Failed to notify approvers: {e}")

# Global instance for use across the application
approval_workflow = AIDecisionApprovalWorkflow()