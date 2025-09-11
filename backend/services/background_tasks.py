"""
Background tasks for budget monitoring and system maintenance
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List

from backend.app.dependencies import get_db
from backend.database.models import Campaign, User, CampaignStatus, BudgetAlert
from .budget_monitoring_service import BudgetMonitoringService
from .rate_limit_service import RateLimitService

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    """Service for running background monitoring and maintenance tasks"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start_monitoring(self):
        """Start all background monitoring tasks"""
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        self.running = True
        logger.info("Starting background monitoring tasks")
        
        # Start individual monitoring tasks
        self.tasks = [
            asyncio.create_task(self._budget_monitoring_loop()),
            asyncio.create_task(self._campaign_monitoring_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        # Wait for tasks to complete (they run indefinitely)
        await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop all background monitoring tasks"""
        if not self.running:
            return
        
        logger.info("Stopping background monitoring tasks")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to finish
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
    
    async def _budget_monitoring_loop(self):
        """Monitor user and campaign budgets periodically"""
        while self.running:
            try:
                logger.debug("Running budget monitoring cycle")
                
                db: Session = next(get_db())
                monitoring_service = BudgetMonitoringService(db)
                
                # Get all active campaigns
                active_campaigns = (
                    db.query(Campaign)
                    .filter(Campaign.status == CampaignStatus.ACTIVE)
                    .all()
                )
                
                campaign_alerts = 0
                user_alerts = 0
                processed_users = set()
                
                for campaign in active_campaigns:
                    # Monitor individual campaign
                    result = monitoring_service.monitor_campaign_spending(campaign.id)
                    if result.get("alerts_created", 0) > 0:
                        campaign_alerts += result["alerts_created"]
                    
                    # Monitor user spending (avoid duplicates)
                    if campaign.user_id not in processed_users:
                        result = monitoring_service.monitor_user_spending(campaign.user_id)
                        if result.get("alerts_created", 0) > 0:
                            user_alerts += result["alerts_created"]
                        
                        # Check user-defined spending limits
                        limit_alerts = monitoring_service.check_spending_limits(campaign.user_id)
                        user_alerts += len(limit_alerts)
                        
                        processed_users.add(campaign.user_id)
                
                if campaign_alerts > 0 or user_alerts > 0:
                    logger.info(f"Budget monitoring cycle completed: {campaign_alerts} campaign alerts, {user_alerts} user alerts")
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error in budget monitoring loop: {str(e)}")
            
            # Wait 5 minutes between cycles
            await asyncio.sleep(300)
    
    async def _campaign_monitoring_loop(self):
        """Monitor campaign performance and status"""
        while self.running:
            try:
                logger.debug("Running campaign monitoring cycle")
                
                db: Session = next(get_db())
                
                # Check for campaigns that should be paused due to poor performance
                # This is a placeholder for more advanced performance monitoring
                
                # Check for campaigns that have exceeded their duration
                now = datetime.utcnow()
                expired_campaigns = (
                    db.query(Campaign)
                    .filter(
                        Campaign.status == CampaignStatus.ACTIVE,
                        Campaign.end_date <= now
                    )
                    .all()
                )
                
                for campaign in expired_campaigns:
                    campaign.status = CampaignStatus.COMPLETED
                    logger.info(f"Auto-completed expired campaign {campaign.id}")
                
                if expired_campaigns:
                    db.commit()
                    logger.info(f"Auto-completed {len(expired_campaigns)} expired campaigns")
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error in campaign monitoring loop: {str(e)}")
            
            # Wait 10 minutes between cycles
            await asyncio.sleep(600)
    
    async def _cleanup_loop(self):
        """Perform periodic cleanup tasks"""
        while self.running:
            try:
                logger.debug("Running cleanup cycle")
                
                db: Session = next(get_db())
                
                # Clean up old rate limit records
                rate_limit_service = RateLimitService(db)
                deleted_records = rate_limit_service.cleanup_old_records(days_old=7)
                
                if deleted_records > 0:
                    logger.info(f"Cleaned up {deleted_records} old rate limit records")
                
                # Clean up old budget alerts (keep for 30 days)
                cutoff = datetime.utcnow() - timedelta(days=30)
                deleted_alerts = (
                    db.query(BudgetAlert)
                    .filter(BudgetAlert.created_at < cutoff)
                    .delete()
                )
                
                if deleted_alerts > 0:
                    db.commit()
                    logger.info(f"Cleaned up {deleted_alerts} old budget alerts")
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
            
            # Wait 1 hour between cleanup cycles
            await asyncio.sleep(3600)
    
    async def _health_check_loop(self):
        """Perform system health checks"""
        while self.running:
            try:
                logger.debug("Running health check cycle")
                
                db: Session = next(get_db())
                
                # Check database connectivity
                user_count = db.query(func.count(User.id)).scalar()
                campaign_count = db.query(func.count(Campaign.id)).scalar()
                
                # Log system metrics
                logger.info(f"System health: {user_count} users, {campaign_count} campaigns")
                
                # Check for system issues
                # - Too many failed campaigns
                # - High error rates
                # - Resource usage issues
                
                failed_campaigns_24h = (
                    db.query(func.count(Campaign.id))
                    .filter(
                        Campaign.status == CampaignStatus.FAILED,
                        Campaign.created_at >= datetime.utcnow() - timedelta(days=1)
                    )
                    .scalar()
                )
                
                if failed_campaigns_24h > 10:  # Threshold for concern
                    logger.warning(f"High failure rate: {failed_campaigns_24h} failed campaigns in last 24h")
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
            
            # Wait 15 minutes between health checks
            await asyncio.sleep(900)
    
    async def run_budget_audit(self) -> Dict:
        """Run a comprehensive budget audit (on-demand)"""
        try:
            logger.info("Starting comprehensive budget audit")
            
            db: Session = next(get_db())
            monitoring_service = BudgetMonitoringService(db)
            
            # Get all users
            users = db.query(User).filter(User.is_active == True).all()
            
            audit_results = {
                "total_users": len(users),
                "alerts_created": 0,
                "actions_taken": 0,
                "users_over_limit": 0,
                "campaigns_paused": 0,
                "total_spending": 0.0
            }
            
            for user in users:
                # Check user spending
                user_result = monitoring_service.monitor_user_spending(user.id)
                audit_results["alerts_created"] += user_result.get("alerts_created", 0)
                audit_results["total_spending"] += user_result.get("current_spending", 0)
                
                if user_result.get("spending_percentage", 0) > 100:
                    audit_results["users_over_limit"] += 1
                
                # Check spending limits
                limit_alerts = monitoring_service.check_spending_limits(user.id)
                audit_results["alerts_created"] += len(limit_alerts)
                
                # Check user campaigns
                campaigns = (
                    db.query(Campaign)
                    .filter(
                        Campaign.user_id == user.id,
                        Campaign.status == CampaignStatus.ACTIVE
                    )
                    .all()
                )
                
                for campaign in campaigns:
                    campaign_result = monitoring_service.monitor_campaign_spending(campaign.id)
                    audit_results["alerts_created"] += campaign_result.get("alerts_created", 0)
                    
                    if "campaign_paused" in campaign_result.get("actions_taken", []):
                        audit_results["campaigns_paused"] += 1
            
            db.close()
            
            logger.info(f"Budget audit completed: {audit_results}")
            return audit_results
            
        except Exception as e:
            logger.error(f"Error in budget audit: {str(e)}")
            return {"error": str(e)}

# Global instance
background_service = BackgroundTaskService()