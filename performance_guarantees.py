"""
Performance Guarantee & Auto-Optimization System
Monitors campaign performance and automatically optimizes or refunds underperforming campaigns
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

# Import our existing modules
from photo_agent import image_creator
from video_agent import video_from_prompt
from revenue_tracking import RevenueAttributionEngine

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
    """
    
    def __init__(self, db_path: str = "performance_guarantees.db"):
        self.db_path = db_path
        self.revenue_engine = RevenueAttributionEngine()
        self.init_database()
        
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
    
    def init_database(self):
        """Initialize performance tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Performance monitoring table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                industry TEXT,
                check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ctr REAL,
                cpc REAL,
                conversion_rate REAL,
                roi REAL,
                performance_status TEXT,
                needs_optimization BOOLEAN,
                guarantee_met BOOLEAN
            )
        ''')
        
        # Optimization actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                action_type TEXT,
                description TEXT,
                priority INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP
            )
        ''')
        
        # Guarantee violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guarantee_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                violation_type TEXT,
                refund_amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def monitor_campaign_performance(self, campaign_id: str, user_id: str, 
                                         industry: str = 'default') -> PerformanceMetrics:
        """Monitor and analyze campaign performance against guarantees"""
        try:
            # Get current campaign metrics (this would integrate with Meta API)
            metrics = await self._get_campaign_metrics(campaign_id)
            
            # Get industry benchmarks
            benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['default'])
            
            # Calculate performance status
            performance_status = self._calculate_performance_status(metrics, benchmarks)
            
            # Check guarantee compliance
            guarantee_met = self._check_guarantee_compliance(metrics, benchmarks)
            
            # Determine if optimization is needed
            needs_optimization = performance_status in [PerformanceStatus.POOR, PerformanceStatus.CRITICAL]
            
            performance = PerformanceMetrics(
                campaign_id=campaign_id,
                ctr=metrics.get('ctr', 0),
                cpc=metrics.get('cpc', 0),
                conversion_rate=metrics.get('conversion_rate', 0),
                roi=metrics.get('roi', 0),
                industry_benchmark_ctr=benchmarks['ctr'],
                industry_benchmark_cpc=benchmarks['cpc'],
                performance_status=performance_status,
                needs_optimization=needs_optimization,
                guarantee_threshold_met=guarantee_met
            )
            
            # Store performance data
            await self._store_performance_data(performance, user_id, industry)
            
            # If guarantees not met, trigger optimization
            if not guarantee_met:
                await self._trigger_guarantee_violation_process(campaign_id, user_id, performance)
            
            return performance
            
        except Exception as e:
            print(f"❌ Error monitoring campaign performance: {e}")
            return PerformanceMetrics(campaign_id, 0, 0, 0, 0, 0, 0, PerformanceStatus.CRITICAL, True, False)
    
    async def _get_campaign_metrics(self, campaign_id: str) -> Dict[str, float]:
        """Get campaign metrics from various sources"""
        # This would integrate with Meta Marketing API, Google Analytics, etc.
        # For demo, we'll simulate realistic metrics
        
        import random
        
        # Simulate campaign metrics with some randomness
        base_metrics = {
            'ctr': random.uniform(1.2, 3.5),
            'cpc': random.uniform(0.85, 4.25),
            'conversion_rate': random.uniform(3.0, 25.0),
            'impressions': random.randint(1000, 50000),
            'clicks': random.randint(50, 1500),
            'spend': random.uniform(50, 2000)
        }
        
        # Calculate ROI using revenue tracking system
        roi_data = await self.revenue_engine.calculate_campaign_roi(campaign_id, base_metrics['spend'])
        base_metrics['roi'] = roi_data.roi_percentage
        
        return base_metrics
    
    def _calculate_performance_status(self, metrics: Dict[str, float], 
                                    benchmarks: Dict[str, float]) -> PerformanceStatus:
        """Determine performance status vs benchmarks"""
        ctr_ratio = metrics.get('ctr', 0) / benchmarks['ctr']
        roi = metrics.get('roi', 0)
        conversion_rate_ratio = metrics.get('conversion_rate', 0) / benchmarks['conversion_rate']
        
        # Score based on multiple factors
        performance_score = (ctr_ratio * 0.4 + (roi / 100) * 0.4 + conversion_rate_ratio * 0.2)
        
        if performance_score >= 1.5:
            return PerformanceStatus.EXCELLENT
        elif performance_score >= 1.0:
            return PerformanceStatus.GOOD
        elif performance_score >= 0.6:
            return PerformanceStatus.POOR
        else:
            return PerformanceStatus.CRITICAL
    
    def _check_guarantee_compliance(self, metrics: Dict[str, float], 
                                  benchmarks: Dict[str, float]) -> bool:
        """Check if campaign meets our performance guarantees"""
        ctr_target = benchmarks['ctr'] * self.guarantees['ctr_improvement']
        roi_target = self.guarantees['roi_threshold']
        
        ctr_met = metrics.get('ctr', 0) >= ctr_target
        roi_met = metrics.get('roi', 0) >= roi_target
        
        return ctr_met and roi_met
    
    async def _store_performance_data(self, performance: PerformanceMetrics, 
                                    user_id: str, industry: str):
        """Store performance monitoring data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaign_performance 
            (campaign_id, user_id, industry, ctr, cpc, conversion_rate, roi, 
             performance_status, needs_optimization, guarantee_met)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            performance.campaign_id, user_id, industry,
            performance.ctr, performance.cpc, performance.conversion_rate, performance.roi,
            performance.performance_status.value, performance.needs_optimization, 
            performance.guarantee_threshold_met
        ))
        
        conn.commit()
        conn.close()
    
    async def _trigger_guarantee_violation_process(self, campaign_id: str, user_id: str, 
                                                 performance: PerformanceMetrics):
        """Handle guarantee violations"""
        print(f"⚠️  Performance guarantee violation detected for campaign {campaign_id}")
        
        # Generate optimization recommendations
        optimizations = await self.generate_optimization_recommendations(campaign_id, performance)
        
        # Store optimization actions
        for optimization in optimizations:
            await self._store_optimization_action(campaign_id, optimization)
        
        # If critical performance, prepare for refund
        if performance.performance_status == PerformanceStatus.CRITICAL:
            await self._prepare_refund_process(campaign_id, user_id)
    
    async def generate_optimization_recommendations(self, campaign_id: str, 
                                                  performance: PerformanceMetrics) -> List[OptimizationAction]:
        """Generate AI-powered optimization recommendations"""
        recommendations = []
        
        # Low CTR - Creative refresh needed
        if performance.ctr < performance.industry_benchmark_ctr:
            recommendations.append(OptimizationAction(
                action_type='creative_refresh',
                description=f'Create new AI-generated creatives to improve CTR from {performance.ctr:.2f}% to {performance.industry_benchmark_ctr:.2f}%+',
                priority=4,
                estimated_impact='30-60% CTR improvement'
            ))
        
        # High CPC - Audience optimization
        if performance.cpc > performance.industry_benchmark_cpc * 1.5:
            recommendations.append(OptimizationAction(
                action_type='audience_adjust',
                description=f'Optimize audience targeting to reduce CPC from ${performance.cpc:.2f} to ${performance.industry_benchmark_cpc:.2f}',
                priority=3,
                estimated_impact='20-40% CPC reduction'
            ))
        
        # Low ROI - Budget reallocation
        if performance.roi < 200:
            recommendations.append(OptimizationAction(
                action_type='budget_realloc',
                description=f'Reallocate budget to higher-performing ad sets to improve ROI from {performance.roi:.1f}% to 200%+',
                priority=5,
                estimated_impact='50-100% ROI improvement'
            ))
        
        # Critical performance - Full refund
        if performance.performance_status == PerformanceStatus.CRITICAL:
            recommendations.append(OptimizationAction(
                action_type='refund',
                description='Campaign performance critically below guarantees - preparing refund process',
                priority=5,
                estimated_impact='Customer retention via guarantee fulfillment'
            ))
        
        return recommendations
    
    async def _store_optimization_action(self, campaign_id: str, action: OptimizationAction):
        """Store optimization recommendation in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO optimization_actions 
            (campaign_id, action_type, description, priority)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, action.action_type, action.description, action.priority))
        
        conn.commit()
        conn.close()
    
    async def auto_optimize_campaign(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Automatically execute optimization recommendations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get pending optimization actions
            cursor.execute('''
                SELECT action_type, description, priority
                FROM optimization_actions 
                WHERE campaign_id = ? AND status = 'pending'
                ORDER BY priority DESC
            ''', (campaign_id,))
            
            actions = cursor.fetchall()
            conn.close()
            
            optimization_results = []
            
            for action in actions:
                action_type, description, priority = action
                result = await self._execute_optimization(campaign_id, action_type, user_id)
                optimization_results.append({
                    'action': action_type,
                    'description': description,
                    'priority': priority,
                    'result': result
                })
            
            return {
                'campaign_id': campaign_id,
                'optimizations_executed': len(optimization_results),
                'results': optimization_results,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error in auto optimization: {e}")
            return {'campaign_id': campaign_id, 'success': False, 'error': str(e)}
    
    async def _execute_optimization(self, campaign_id: str, action_type: str, user_id: str) -> Dict[str, Any]:
        """Execute specific optimization action"""
        try:
            if action_type == 'creative_refresh':
                # Generate new AI creative variations
                new_creative = await self._generate_new_creative(campaign_id)
                return {
                    'status': 'completed',
                    'new_asset': new_creative,
                    'message': 'New AI-generated creative created'
                }
                
            elif action_type == 'audience_adjust':
                # This would integrate with Meta API to adjust targeting
                return {
                    'status': 'completed',
                    'message': 'Audience targeting optimized based on performance data'
                }
                
            elif action_type == 'budget_realloc':
                # This would integrate with Meta API to reallocate budget
                return {
                    'status': 'completed',
                    'message': 'Budget reallocated to higher-performing ad sets'
                }
                
            elif action_type == 'refund':
                # Process refund
                refund_result = await self._process_refund(campaign_id, user_id)
                return refund_result
                
            return {'status': 'unknown_action', 'message': f'Unknown action type: {action_type}'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _generate_new_creative(self, campaign_id: str) -> str:
        """Generate new AI creative for underperforming campaign"""
        # Get campaign details to understand what type of creative to generate
        prompt = "A high-converting marketing image with bold colors and clear call-to-action"
        
        # Generate new image using our AI system
        new_image = await image_creator(prompt, "hyperrealistic marketing poster")
        
        if new_image:
            print(f"✅ Generated new creative: {new_image}")
            return new_image
        else:
            print("❌ Failed to generate new creative")
            return ""
    
    async def _prepare_refund_process(self, campaign_id: str, user_id: str):
        """Prepare refund for guarantee violation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate refund amount based on campaign spend
        roi_data = await self.revenue_engine.calculate_campaign_roi(campaign_id)
        refund_amount = roi_data.total_spend * 0.5  # 50% refund for guarantee violation
        
        cursor.execute('''
            INSERT INTO guarantee_violations 
            (campaign_id, user_id, violation_type, refund_amount)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, user_id, 'performance_guarantee', refund_amount))
        
        conn.commit()
        conn.close()
        
        print(f"💰 Refund prepared: ${refund_amount:.2f} for campaign {campaign_id}")
    
    async def _process_refund(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        """Process actual refund (would integrate with payment processor)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT refund_amount FROM guarantee_violations 
                WHERE campaign_id = ? AND user_id = ? AND status = 'pending'
            ''', (campaign_id, user_id))
            
            result = cursor.fetchone()
            if result:
                refund_amount = result[0]
                
                # Update status to processed
                cursor.execute('''
                    UPDATE guarantee_violations 
                    SET status = 'processed', resolved_at = CURRENT_TIMESTAMP
                    WHERE campaign_id = ? AND user_id = ?
                ''', (campaign_id, user_id))
                
                conn.commit()
                conn.close()
                
                return {
                    'status': 'completed',
                    'refund_amount': refund_amount,
                    'message': f'Refund of ${refund_amount:.2f} processed for performance guarantee violation'
                }
            
            conn.close()
            return {'status': 'no_refund_due', 'message': 'No pending refunds found'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def get_performance_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance dashboard for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall performance summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_campaigns,
                    AVG(ctr) as avg_ctr,
                    AVG(roi) as avg_roi,
                    SUM(CASE WHEN guarantee_met = 1 THEN 1 ELSE 0 END) as guarantees_met,
                    SUM(CASE WHEN needs_optimization = 1 THEN 1 ELSE 0 END) as needs_optimization
                FROM campaign_performance 
                WHERE user_id = ? AND check_date >= date('now', '-30 days')
            ''', (user_id,))
            
            summary = cursor.fetchone()
            
            # Recent performance trends
            cursor.execute('''
                SELECT 
                    DATE(check_date) as date,
                    AVG(ctr) as daily_ctr,
                    AVG(roi) as daily_roi,
                    COUNT(*) as campaigns_checked
                FROM campaign_performance 
                WHERE user_id = ? AND check_date >= date('now', '-7 days')
                GROUP BY DATE(check_date)
                ORDER BY date DESC
            ''', (user_id,))
            
            trends = cursor.fetchall()
            
            # Optimization actions status
            cursor.execute('''
                SELECT 
                    action_type,
                    COUNT(*) as count,
                    status
                FROM optimization_actions oa
                JOIN campaign_performance cp ON oa.campaign_id = cp.campaign_id
                WHERE cp.user_id = ? AND oa.created_at >= date('now', '-30 days')
                GROUP BY action_type, status
            ''', (user_id,))
            
            optimizations = cursor.fetchall()
            
            conn.close()
            
            return {
                'summary': {
                    'total_campaigns': summary[0] or 0,
                    'avg_ctr': round(summary[1] or 0, 2),
                    'avg_roi': round(summary[2] or 0, 1),
                    'guarantee_success_rate': round((summary[3] or 0) / max(summary[0] or 1, 1) * 100, 1),
                    'campaigns_optimized': summary[4] or 0
                },
                'recent_trends': [
                    {
                        'date': row[0],
                        'avg_ctr': round(row[1] or 0, 2),
                        'avg_roi': round(row[2] or 0, 1),
                        'campaigns': row[3]
                    } for row in trends
                ],
                'optimization_status': [
                    {
                        'action_type': row[0],
                        'count': row[1],
                        'status': row[2]
                    } for row in optimizations
                ]
            }
            
        except Exception as e:
            print(f"❌ Error getting performance dashboard: {e}")
            return {}

# Helper functions for easy integration
async def monitor_campaign(campaign_id: str, user_id: str, industry: str = 'default'):
    """Quick campaign monitoring"""
    engine = PerformanceGuaranteeEngine()
    return await engine.monitor_campaign_performance(campaign_id, user_id, industry)

async def auto_optimize(campaign_id: str, user_id: str):
    """Quick auto-optimization"""
    engine = PerformanceGuaranteeEngine()
    return await engine.auto_optimize_campaign(campaign_id, user_id)

async def get_dashboard(user_id: str):
    """Quick performance dashboard"""
    engine = PerformanceGuaranteeEngine()
    return await engine.get_performance_dashboard(user_id)

async def main():
    """Test the performance guarantee system"""
    print("🎯 Performance Guarantee & Auto-Optimization System")
    print("=" * 55)
    
    engine = PerformanceGuaranteeEngine()
    
    # Demo: Monitor campaign performance
    campaign_id = f"camp_{int(datetime.now().timestamp())}"
    user_id = "user_123"
    
    print(f"🔍 Monitoring campaign {campaign_id}...")
    performance = await engine.monitor_campaign_performance(campaign_id, user_id, 'restaurant')
    
    print(f"📊 Performance Status: {performance.performance_status.value}")
    print(f"📈 CTR: {performance.ctr:.2f}% (Benchmark: {performance.industry_benchmark_ctr:.2f}%)")
    print(f"💰 ROI: {performance.roi:.1f}%")
    print(f"✅ Guarantee Met: {performance.guarantee_threshold_met}")
    
    if performance.needs_optimization:
        print(f"\n🔧 Auto-optimizing campaign...")
        optimization_result = await engine.auto_optimize_campaign(campaign_id, user_id)
        print(f"✅ Optimizations executed: {optimization_result['optimizations_executed']}")
    
    # Demo: Performance dashboard
    dashboard = await engine.get_performance_dashboard(user_id)
    print(f"\n📊 Performance Dashboard:")
    print(json.dumps(dashboard, indent=2))

if __name__ == "__main__":
    asyncio.run(main())