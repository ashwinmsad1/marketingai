"""
Revenue Attribution & ROI Tracking System
Tracks every lead/sale back to specific AI-generated content
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import uuid

@dataclass
class CampaignConversion:
    """Data structure for campaign conversions"""
    conversion_id: str
    campaign_id: str
    user_id: str
    conversion_type: str  # 'lead', 'sale', 'signup', 'download'
    value: float
    timestamp: datetime
    source_platform: str  # 'facebook', 'instagram'
    creative_asset: str  # path to AI-generated content
    attribution_window: int = 7  # days

@dataclass
class ROIMetrics:
    """ROI calculation results"""
    campaign_id: str
    total_spend: float
    total_revenue: float
    roi_percentage: float
    cost_per_conversion: float
    conversion_count: int
    lifetime_value: float

class RevenueAttributionEngine:
    """
    Complete revenue tracking and attribution system
    """
    
    def __init__(self, db_path: str = "revenue_tracking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for revenue tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                campaign_name TEXT,
                creative_asset TEXT,
                platform TEXT,
                total_spend REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                conversion_id TEXT PRIMARY KEY,
                campaign_id TEXT,
                user_id TEXT,
                conversion_type TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_platform TEXT,
                attribution_window INTEGER DEFAULT 7,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (campaign_id)
            )
        ''')
        
        # Customer lifetime value table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_ltv (
                customer_id TEXT PRIMARY KEY,
                user_id TEXT,
                first_conversion_campaign TEXT,
                total_lifetime_value REAL DEFAULT 0,
                conversion_count INTEGER DEFAULT 0,
                first_conversion_date TIMESTAMP,
                last_conversion_date TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def track_campaign_launch(self, campaign_id: str, user_id: str, campaign_name: str, 
                                  creative_asset: str, platform: str) -> bool:
        """Track new campaign launch"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO campaigns 
                (campaign_id, user_id, campaign_name, creative_asset, platform)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, user_id, campaign_name, creative_asset, platform))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Campaign {campaign_id} tracked for revenue attribution")
            return True
            
        except Exception as e:
            print(f"❌ Error tracking campaign launch: {e}")
            return False
    
    async def track_conversion(self, campaign_id: str, conversion_type: str, 
                             value: float, customer_id: Optional[str] = None) -> str:
        """Track a conversion and attribute it to a campaign"""
        try:
            conversion_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute('SELECT user_id, platform FROM campaigns WHERE campaign_id = ?', (campaign_id,))
            campaign_data = cursor.fetchone()
            
            if not campaign_data:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            user_id, platform = campaign_data
            
            # Insert conversion
            cursor.execute('''
                INSERT INTO conversions 
                (conversion_id, campaign_id, user_id, conversion_type, value, source_platform)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversion_id, campaign_id, user_id, conversion_type, value, platform))
            
            # Update customer LTV if customer_id provided
            if customer_id:
                await self._update_customer_ltv(cursor, customer_id, user_id, campaign_id, value)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Conversion tracked: {conversion_type} worth ${value} from campaign {campaign_id}")
            return conversion_id
            
        except Exception as e:
            print(f"❌ Error tracking conversion: {e}")
            return ""
    
    async def _update_customer_ltv(self, cursor, customer_id: str, user_id: str, 
                                 campaign_id: str, value: float):
        """Update customer lifetime value"""
        cursor.execute('SELECT total_lifetime_value, conversion_count FROM customer_ltv WHERE customer_id = ?', 
                      (customer_id,))
        existing = cursor.fetchone()
        
        if existing:
            new_ltv = existing[0] + value
            new_count = existing[1] + 1
            cursor.execute('''
                UPDATE customer_ltv 
                SET total_lifetime_value = ?, conversion_count = ?, last_conversion_date = CURRENT_TIMESTAMP
                WHERE customer_id = ?
            ''', (new_ltv, new_count, customer_id))
        else:
            cursor.execute('''
                INSERT INTO customer_ltv 
                (customer_id, user_id, first_conversion_campaign, total_lifetime_value, conversion_count,
                 first_conversion_date, last_conversion_date)
                VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (customer_id, user_id, campaign_id, value))
    
    async def calculate_campaign_roi(self, campaign_id: str, ad_spend: float = 0) -> ROIMetrics:
        """Calculate comprehensive ROI metrics for a campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total revenue from conversions
            cursor.execute('''
                SELECT COUNT(*), SUM(value), AVG(value)
                FROM conversions 
                WHERE campaign_id = ?
            ''', (campaign_id,))
            
            result = cursor.fetchone()
            conversion_count = result[0] or 0
            total_revenue = result[1] or 0
            avg_conversion_value = result[2] or 0
            
            # Update campaign spend if provided
            if ad_spend > 0:
                cursor.execute('UPDATE campaigns SET total_spend = ? WHERE campaign_id = ?', 
                             (ad_spend, campaign_id))
                conn.commit()
            
            # Get campaign spend
            cursor.execute('SELECT total_spend FROM campaigns WHERE campaign_id = ?', (campaign_id,))
            spend_result = cursor.fetchone()
            total_spend = spend_result[0] if spend_result else ad_spend
            
            conn.close()
            
            # Calculate metrics
            roi_percentage = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
            cost_per_conversion = total_spend / conversion_count if conversion_count > 0 else 0
            
            # Estimate lifetime value (simple model)
            lifetime_value = avg_conversion_value * 3.5  # Average customer makes 3.5 purchases
            
            return ROIMetrics(
                campaign_id=campaign_id,
                total_spend=total_spend,
                total_revenue=total_revenue,
                roi_percentage=roi_percentage,
                cost_per_conversion=cost_per_conversion,
                conversion_count=conversion_count,
                lifetime_value=lifetime_value
            )
            
        except Exception as e:
            print(f"❌ Error calculating ROI: {e}")
            return ROIMetrics(campaign_id, 0, 0, 0, 0, 0, 0)
    
    async def generate_success_report(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive success report for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Campaign performance
            cursor.execute('''
                SELECT c.campaign_id, c.campaign_name, c.creative_asset, c.total_spend,
                       COUNT(conv.conversion_id) as conversions,
                       SUM(conv.value) as revenue
                FROM campaigns c
                LEFT JOIN conversions conv ON c.campaign_id = conv.campaign_id
                WHERE c.user_id = ? AND c.created_at >= ?
                GROUP BY c.campaign_id
                ORDER BY revenue DESC
            ''', (user_id, start_date))
            
            campaigns = cursor.fetchall()
            
            # Overall metrics
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT c.campaign_id) as total_campaigns,
                    SUM(c.total_spend) as total_spend,
                    COUNT(conv.conversion_id) as total_conversions,
                    SUM(conv.value) as total_revenue
                FROM campaigns c
                LEFT JOIN conversions conv ON c.campaign_id = conv.campaign_id
                WHERE c.user_id = ? AND c.created_at >= ?
            ''', (user_id, start_date))
            
            overall = cursor.fetchone()
            
            # Top performing creative assets
            cursor.execute('''
                SELECT c.creative_asset, COUNT(conv.conversion_id) as conversions, 
                       SUM(conv.value) as revenue
                FROM campaigns c
                LEFT JOIN conversions conv ON c.campaign_id = conv.campaign_id
                WHERE c.user_id = ? AND c.created_at >= ?
                GROUP BY c.creative_asset
                ORDER BY revenue DESC
                LIMIT 5
            ''', (user_id, start_date))
            
            top_creatives = cursor.fetchall()
            
            conn.close()
            
            # Calculate overall ROI
            total_spend = overall[1] or 0
            total_revenue = overall[3] or 0
            overall_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
            
            return {
                'report_period': f'{days} days',
                'generated_at': datetime.now().isoformat(),
                'overall_metrics': {
                    'total_campaigns': overall[0] or 0,
                    'total_spend': total_spend,
                    'total_conversions': overall[2] or 0,
                    'total_revenue': total_revenue,
                    'overall_roi': round(overall_roi, 2),
                    'avg_cost_per_conversion': total_spend / (overall[2] or 1)
                },
                'campaign_performance': [
                    {
                        'campaign_id': row[0],
                        'name': row[1],
                        'creative_asset': row[2],
                        'spend': row[3] or 0,
                        'conversions': row[4] or 0,
                        'revenue': row[5] or 0,
                        'roi': ((row[5] or 0) - (row[3] or 0)) / (row[3] or 1) * 100
                    } for row in campaigns
                ],
                'top_performing_creatives': [
                    {
                        'asset': row[0],
                        'conversions': row[1],
                        'revenue': row[2] or 0
                    } for row in top_creatives
                ]
            }
            
        except Exception as e:
            print(f"❌ Error generating success report: {e}")
            return {}
    
    async def track_lead_source(self, lead_data: Dict[str, Any]) -> bool:
        """Track lead source from external forms/webhooks"""
        try:
            # Extract campaign ID from lead source or referrer
            campaign_id = lead_data.get('campaign_id') or lead_data.get('utm_campaign')
            
            if campaign_id:
                conversion_id = await self.track_conversion(
                    campaign_id=campaign_id,
                    conversion_type='lead',
                    value=lead_data.get('estimated_value', 50.0),  # Default lead value
                    customer_id=lead_data.get('email') or lead_data.get('phone')
                )
                return bool(conversion_id)
            
            return False
            
        except Exception as e:
            print(f"❌ Error tracking lead source: {e}")
            return False
    
    async def get_attribution_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights on which AI content performs best"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Creative asset performance
            cursor.execute('''
                SELECT 
                    c.creative_asset,
                    c.platform,
                    COUNT(conv.conversion_id) as conversions,
                    SUM(conv.value) as revenue,
                    AVG(conv.value) as avg_conversion_value
                FROM campaigns c
                LEFT JOIN conversions conv ON c.campaign_id = conv.campaign_id
                WHERE c.user_id = ?
                GROUP BY c.creative_asset, c.platform
                ORDER BY revenue DESC
            ''', (user_id,))
            
            asset_performance = cursor.fetchall()
            
            # Platform comparison
            cursor.execute('''
                SELECT 
                    c.platform,
                    COUNT(DISTINCT c.campaign_id) as campaigns,
                    COUNT(conv.conversion_id) as conversions,
                    SUM(conv.value) as revenue,
                    AVG(conv.value) as avg_conversion_value
                FROM campaigns c
                LEFT JOIN conversions conv ON c.campaign_id = conv.campaign_id
                WHERE c.user_id = ?
                GROUP BY c.platform
            ''', (user_id,))
            
            platform_performance = cursor.fetchall()
            
            conn.close()
            
            return {
                'creative_insights': [
                    {
                        'asset': row[0],
                        'platform': row[1],
                        'conversions': row[2],
                        'revenue': row[3] or 0,
                        'avg_conversion_value': row[4] or 0
                    } for row in asset_performance
                ],
                'platform_comparison': [
                    {
                        'platform': row[0],
                        'campaigns': row[1],
                        'conversions': row[2],
                        'revenue': row[3] or 0,
                        'avg_conversion_value': row[4] or 0
                    } for row in platform_performance
                ]
            }
            
        except Exception as e:
            print(f"❌ Error getting attribution insights: {e}")
            return {}

# Helper functions for easy integration
async def track_campaign_success(campaign_id: str, user_id: str, campaign_name: str, 
                               creative_asset: str, platform: str):
    """Quick campaign tracking setup"""
    engine = RevenueAttributionEngine()
    return await engine.track_campaign_launch(campaign_id, user_id, campaign_name, creative_asset, platform)

async def record_conversion(campaign_id: str, conversion_type: str, value: float, customer_id: str = None):
    """Quick conversion recording"""
    engine = RevenueAttributionEngine()
    return await engine.track_conversion(campaign_id, conversion_type, value, customer_id)

async def get_campaign_roi(campaign_id: str, ad_spend: float = 0) -> Dict[str, Any]:
    """Quick ROI calculation"""
    engine = RevenueAttributionEngine()
    roi_metrics = await engine.calculate_campaign_roi(campaign_id, ad_spend)
    return asdict(roi_metrics)

async def main():
    """Test the revenue attribution system"""
    print("💰 Revenue Attribution & ROI Tracking System")
    print("=" * 50)
    
    engine = RevenueAttributionEngine()
    
    # Demo: Track a campaign
    campaign_id = f"camp_{int(datetime.now().timestamp())}"
    await engine.track_campaign_launch(
        campaign_id=campaign_id,
        user_id="user_123",
        campaign_name="Restaurant Promotion",
        creative_asset="hyperrealistic_food_poster.png",
        platform="facebook"
    )
    
    # Demo: Track conversions
    await engine.track_conversion(campaign_id, "lead", 50.0, "customer@example.com")
    await engine.track_conversion(campaign_id, "sale", 150.0, "customer@example.com")
    
    # Demo: Calculate ROI
    roi_metrics = await engine.calculate_campaign_roi(campaign_id, 100.0)
    print(f"\n📊 Campaign ROI: {roi_metrics.roi_percentage:.2f}%")
    print(f"💰 Revenue: ${roi_metrics.total_revenue}")
    print(f"💸 Cost per conversion: ${roi_metrics.cost_per_conversion:.2f}")
    
    # Demo: Success report
    report = await engine.generate_success_report("user_123")
    print(f"\n📈 Success Report:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())