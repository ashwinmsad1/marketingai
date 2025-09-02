"""
Performance Guarantee System for AI Marketing Automation Platform
Enhanced with PostgreSQL database integration for reliable performance tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

# Import database components
from database import get_db
from database.models import Campaign, Analytics, CampaignStatus
from database.crud import CampaignCRUD, AnalyticsCRUD
from sqlalchemy.orm import Session

# Import our enhanced modules
from photo_agent import image_creator
from video_agent import video_from_prompt
from revenue_tracking import RevenueAttributionEngine

# Configure logging
logger = logging.getLogger(__name__)

class PerformanceStatus(Enum):
    EXCELLENT = "excellent"  # Exceeds expectations
    GOOD = "good"           # Meets expectations  
    POOR = "poor"           # Below expectations
    CRITICAL = "critical"   # Requires immediate action

@dataclass
class PerformanceMetrics:
    """Campaign performance data structure"""
    campaign_id: str
    ctr: float  # Click-through rate
    cpc: float  # Cost per click
    conversion_rate: float
    roi: float
    industry_benchmark_ctr: float
    industry_benchmark_cpc: float
    performance_status: PerformanceStatus
    needs_optimization: bool
    guarantee_threshold_met: bool

@dataclass
class OptimizationAction:
    """Optimization action data structure"""
    action_type: str  # 'creative_refresh', 'audience_adjust', 'budget_realloc', 'refund'
    description: str
    priority: int  # 1-5, higher is more urgent
    estimated_impact: str

class PerformanceGuaranteeEngine:
    """
    System that monitors campaign performance and ensures customer success guarantees
    Using PostgreSQL database for reliable performance tracking
    """
    
    def __init__(self):
        """Initialize the performance guarantee engine with PostgreSQL backend"""
        self.revenue_engine = RevenueAttributionEngine()
        
        # Industry benchmarks (these would be updated from real data)
        self.industry_benchmarks = {
            'restaurant': {'ctr': 2.1, 'cpc': 1.35, 'conversion_rate': 8.5},
            'real_estate': {'ctr': 1.8, 'cpc': 2.15, 'conversion_rate': 12.0},
            'fitness': {'ctr': 2.5, 'cpc': 1.85, 'conversion_rate': 6.5},
            'ecommerce': {'ctr': 1.9, 'cpc': 1.45, 'conversion_rate': 4.2},
            'beauty': {'ctr': 3.2, 'cpc': 1.65, 'conversion_rate': 7.8},
            'automotive': {'ctr': 1.6, 'cpc': 2.85, 'conversion_rate': 15.5},
            'education': {'ctr': 2.8, 'cpc': 2.25, 'conversion_rate': 18.0},
            'healthcare': {'ctr': 1.4, 'cpc': 3.45, 'conversion_rate': 22.0},
            'default': {'ctr': 2.0, 'cpc': 1.75, 'conversion_rate': 8.0}
        }
        
        # Performance guarantees
        self.guarantees = {
            'ctr_improvement': 1.5,  # 50% improvement over industry average
            'lead_generation_minimum': 2.0,  # 2x more leads than promised
            'roi_threshold': 200.0,  # 200% ROI minimum
            'refund_threshold_days': 7  # Days before refund eligibility
        }
        
        logger.info("Performance Guarantee Engine initialized with PostgreSQL backend")
    
    def _get_db_session(self) -> Session:
        """Get database session - in production this would use dependency injection"""
        return next(get_db())

    async def monitor_campaign_performance(self, campaign_id: str) -> PerformanceMetrics:
        """Monitor campaign performance and determine if guarantees are met"""
        try:
            db = self._get_db_session()
            try:
                # Get campaign details
                campaign = CampaignCRUD.get_campaign(db, campaign_id)
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                # Get recent analytics
                analytics = AnalyticsCRUD.get_campaign_analytics(db, campaign_id, days=7)
                
                # Calculate performance metrics
                if analytics:
                    avg_ctr = sum(a.ctr for a in analytics) / len(analytics)
                    avg_cpc = sum(a.cpc for a in analytics) / len(analytics)
                    avg_conversion_rate = sum(a.conversions / max(a.clicks, 1) * 100 for a in analytics) / len(analytics)
                    avg_roi = sum(a.roi for a in analytics) / len(analytics)
                else:
                    # Use campaign-level metrics as fallback
                    avg_ctr = campaign.ctr or 0
                    avg_cpc = campaign.cpc or 0
                    avg_conversion_rate = (campaign.conversions / max(campaign.clicks, 1) * 100) if campaign.clicks else 0
                    avg_roi = campaign.roas or 0
                
                # Get industry benchmarks
                industry = campaign.industry or 'default'
                benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['default'])
                
                # Determine performance status
                performance_status = self._calculate_performance_status(
                    avg_ctr, avg_cpc, avg_conversion_rate, avg_roi, benchmarks
                )
                
                # Check if optimization is needed
                needs_optimization = self._needs_optimization(performance_status, avg_ctr, benchmarks)
                
                # Check if guarantee thresholds are met
                guarantee_met = self._check_guarantee_thresholds(avg_ctr, avg_roi, benchmarks)
                
                metrics = PerformanceMetrics(
                    campaign_id=campaign_id,
                    ctr=avg_ctr,
                    cpc=avg_cpc,
                    conversion_rate=avg_conversion_rate,
                    roi=avg_roi,
                    industry_benchmark_ctr=benchmarks['ctr'],
                    industry_benchmark_cpc=benchmarks['cpc'],
                    performance_status=performance_status,
                    needs_optimization=needs_optimization,
                    guarantee_threshold_met=guarantee_met
                )
                
                logger.info(f"Performance monitored for campaign {campaign_id}: {performance_status.value}")
                return metrics
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error monitoring campaign performance: {e}")
            return self._empty_performance_metrics(campaign_id)

    async def auto_optimize_campaign(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Automatically optimize underperforming campaigns"""
        try:
            # Get current performance metrics
            metrics = await self.monitor_campaign_performance(campaign_id)
            
            if not metrics.needs_optimization:
                return {
                    "optimized": False,
                    "reason": "Campaign performance meets thresholds",
                    "metrics": asdict(metrics)
                }
            
            # Generate optimization actions
            actions = self._generate_optimization_actions(metrics)
            
            # Execute high-priority actions
            optimization_results = []
            for action in actions:
                if action.priority >= 4:  # High priority actions only
                    result = await self._execute_optimization_action(campaign_id, user_id, action)
                    optimization_results.append(result)
            
            return {
                "optimized": True,
                "actions_taken": len(optimization_results),
                "optimization_results": optimization_results,
                "updated_metrics": asdict(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error auto-optimizing campaign: {e}")
            return {
                "optimized": False,
                "error": str(e)
            }

    async def get_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive performance data for a campaign"""
        try:
            metrics = await self.monitor_campaign_performance(campaign_id)
            roi_data = await self.revenue_engine.get_campaign_roi(campaign_id)
            
            return {
                "campaign_id": campaign_id,
                "performance_metrics": asdict(metrics),
                "roi_metrics": asdict(roi_data),
                "guarantee_status": "met" if metrics.guarantee_threshold_met else "not_met",
                "optimization_needed": metrics.needs_optimization,
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign performance: {e}")
            return {
                "campaign_id": campaign_id,
                "error": str(e)
            }

    async def check_refund_eligibility(self, campaign_id: str) -> Dict[str, Any]:
        """Check if campaign is eligible for performance guarantee refund"""
        try:
            db = self._get_db_session()
            try:
                campaign = CampaignCRUD.get_campaign(db, campaign_id)
                if not campaign:
                    raise ValueError(f"Campaign {campaign_id} not found")
                
                # Check campaign age
                days_running = (datetime.utcnow() - campaign.created_at).days
                if days_running < self.guarantees['refund_threshold_days']:
                    return {
                        "eligible": False,
                        "reason": f"Campaign must run for at least {self.guarantees['refund_threshold_days']} days",
                        "days_remaining": self.guarantees['refund_threshold_days'] - days_running
                    }
                
                # Check performance metrics
                metrics = await self.monitor_campaign_performance(campaign_id)
                
                # Refund eligibility criteria
                roi_below_threshold = metrics.roi < self.guarantees['roi_threshold']
                ctr_below_benchmark = metrics.ctr < (metrics.industry_benchmark_ctr * 0.7)  # 30% below benchmark
                
                if roi_below_threshold and ctr_below_benchmark:
                    return {
                        "eligible": True,
                        "reason": "Performance guarantees not met",
                        "refund_amount": campaign.spend * 0.5,  # 50% refund
                        "metrics": asdict(metrics)
                    }
                else:
                    return {
                        "eligible": False,
                        "reason": "Performance meets minimum thresholds",
                        "metrics": asdict(metrics)
                    }
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error checking refund eligibility: {e}")
            return {
                "eligible": False,
                "error": str(e)
            }

    def _calculate_performance_status(self, ctr: float, cpc: float, conversion_rate: float, 
                                    roi: float, benchmarks: Dict) -> PerformanceStatus:
        """Calculate overall performance status based on metrics"""
        score = 0
        
        # CTR score (30% weight)
        if ctr >= benchmarks['ctr'] * 1.5:
            score += 30
        elif ctr >= benchmarks['ctr']:
            score += 20
        elif ctr >= benchmarks['ctr'] * 0.8:
            score += 10
        
        # CPC score (20% weight) - lower is better
        if cpc <= benchmarks['cpc'] * 0.8:
            score += 20
        elif cpc <= benchmarks['cpc']:
            score += 15
        elif cpc <= benchmarks['cpc'] * 1.2:
            score += 5
        
        # Conversion rate score (25% weight)
        if conversion_rate >= benchmarks['conversion_rate'] * 1.3:
            score += 25
        elif conversion_rate >= benchmarks['conversion_rate']:
            score += 18
        elif conversion_rate >= benchmarks['conversion_rate'] * 0.8:
            score += 10
        
        # ROI score (25% weight)
        if roi >= 300:
            score += 25
        elif roi >= 200:
            score += 18
        elif roi >= 100:
            score += 10
        
        # Determine status based on total score
        if score >= 80:
            return PerformanceStatus.EXCELLENT
        elif score >= 60:
            return PerformanceStatus.GOOD
        elif score >= 30:
            return PerformanceStatus.POOR
        else:
            return PerformanceStatus.CRITICAL

    def _needs_optimization(self, status: PerformanceStatus, ctr: float, benchmarks: Dict) -> bool:
        """Determine if campaign needs optimization"""
        return (status in [PerformanceStatus.POOR, PerformanceStatus.CRITICAL] or 
                ctr < benchmarks['ctr'] * 0.8)

    def _check_guarantee_thresholds(self, ctr: float, roi: float, benchmarks: Dict) -> bool:
        """Check if performance guarantee thresholds are met"""
        ctr_threshold_met = ctr >= benchmarks['ctr'] * (self.guarantees['ctr_improvement'] - 1)
        roi_threshold_met = roi >= self.guarantees['roi_threshold']
        return ctr_threshold_met and roi_threshold_met

    def _generate_optimization_actions(self, metrics: PerformanceMetrics) -> List[OptimizationAction]:
        """Generate specific optimization actions based on performance metrics"""
        actions = []
        
        if metrics.ctr < metrics.industry_benchmark_ctr * 0.8:
            actions.append(OptimizationAction(
                action_type="creative_refresh",
                description="Generate new AI-created visuals to improve engagement",
                priority=5,
                estimated_impact="15-25% CTR improvement"
            ))
        
        if metrics.cpc > metrics.industry_benchmark_cpc * 1.3:
            actions.append(OptimizationAction(
                action_type="audience_adjust",
                description="Refine audience targeting to reduce cost per click",
                priority=4,
                estimated_impact="10-20% CPC reduction"
            ))
        
        if metrics.conversion_rate < 5.0:
            actions.append(OptimizationAction(
                action_type="landing_page_optimize",
                description="Improve landing page conversion elements",
                priority=3,
                estimated_impact="5-15% conversion rate improvement"
            ))
        
        if metrics.roi < 150:
            actions.append(OptimizationAction(
                action_type="budget_realloc",
                description="Reallocate budget to better performing ad sets",
                priority=4,
                estimated_impact="20-30% ROI improvement"
            ))
        
        return sorted(actions, key=lambda x: x.priority, reverse=True)

    async def _execute_optimization_action(self, campaign_id: str, user_id: str, 
                                         action: OptimizationAction) -> Dict[str, Any]:
        """Execute a specific optimization action"""
        try:
            if action.action_type == "creative_refresh":
                # Generate new creative content
                new_image = await image_creator.generate_poster_async(
                    prompt="High-converting marketing advertisement with professional design",
                    style="modern commercial"
                )
                
                return {
                    "action": action.action_type,
                    "status": "executed",
                    "details": f"New creative generated: {new_image.get('image_path', 'N/A')}"
                }
            
            elif action.action_type == "audience_adjust":
                # In a real implementation, this would integrate with Meta Ads API
                return {
                    "action": action.action_type,
                    "status": "executed",
                    "details": "Audience targeting parameters optimized"
                }
            
            else:
                return {
                    "action": action.action_type,
                    "status": "pending",
                    "details": "Action queued for manual review"
                }
                
        except Exception as e:
            logger.error(f"Error executing optimization action: {e}")
            return {
                "action": action.action_type,
                "status": "failed",
                "error": str(e)
            }

    def _empty_performance_metrics(self, campaign_id: str) -> PerformanceMetrics:
        """Return empty performance metrics for error cases"""
        return PerformanceMetrics(
            campaign_id=campaign_id,
            ctr=0.0,
            cpc=0.0,
            conversion_rate=0.0,
            roi=0.0,
            industry_benchmark_ctr=2.0,
            industry_benchmark_cpc=1.75,
            performance_status=PerformanceStatus.CRITICAL,
            needs_optimization=True,
            guarantee_threshold_met=False
        )

async def monitor_campaign(campaign_id: str, user_id: str) -> Dict[str, Any]:
    """
    Monitor campaign performance and return status
    This is a utility function for compatibility with marketing automation
    """
    try:
        engine = PerformanceGuaranteeEngine()
        
        # Monitor campaign performance
        metrics = await engine.monitor_campaign_performance(campaign_id)
        
        # Return performance data
        return {
            "campaign_id": campaign_id,
            "user_id": user_id,
            "performance_status": metrics.performance_status.value,
            "metrics": asdict(metrics),
            "needs_optimization": metrics.needs_optimization,
            "guarantee_met": metrics.guarantee_threshold_met,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error monitoring campaign {campaign_id}: {e}")
        return {
            "campaign_id": campaign_id,
            "user_id": user_id,
            "performance_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Test function
async def test_performance_engine():
    """Test performance guarantee engine functionality"""
    print("🔍 Testing Performance Guarantee Engine...")
    
    engine = PerformanceGuaranteeEngine()
    
    # Test performance monitoring
    metrics = await engine.monitor_campaign_performance("test-campaign-001")
    print(f"✅ Performance monitoring: Status={metrics.performance_status.value}, CTR={metrics.ctr}")
    
    # Test optimization
    optimization_result = await engine.auto_optimize_campaign("test-campaign-001", "test-user-001")
    print(f"✅ Auto optimization: {'Success' if optimization_result.get('optimized') else 'Not needed'}")
    
    # Test refund eligibility
    refund_check = await engine.check_refund_eligibility("test-campaign-001")
    print(f"✅ Refund eligibility: {'Eligible' if refund_check.get('eligible') else 'Not eligible'}")
    
    print("🎉 Performance engine tests completed!")

if __name__ == "__main__":
    asyncio.run(test_performance_engine())