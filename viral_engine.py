"""
Viral Content & Trending Engine
Detects trending topics and creates viral-optimized content automatically
"""

import asyncio
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import random
import re

# Import our AI agents
from photo_agent import image_creator
from video_agent import video_from_prompt

@dataclass
class TrendingTopic:
    """Trending topic data structure"""
    topic_id: str
    topic_name: str
    trend_score: float
    industry: str
    keywords: List[str]
    hashtags: List[str]
    viral_elements: List[str]
    detected_at: datetime
    peak_period: str
    engagement_potential: float

@dataclass
class ViralContent:
    """Viral content template data structure"""
    content_id: str
    topic_id: str
    content_type: str  # 'image', 'video', 'carousel'
    viral_prompt: str
    viral_caption: str
    viral_hashtags: List[str]
    engagement_hooks: List[str]
    optimal_posting_time: str
    virality_score: float

@dataclass
class ViralCampaign:
    """Complete viral campaign data structure"""
    campaign_id: str
    user_id: str
    trending_topic: TrendingTopic
    viral_content: ViralContent
    generated_assets: List[str]
    performance_prediction: Dict[str, float]
    created_at: datetime

class ViralContentEngine:
    """
    AI-powered system for detecting trends and creating viral content
    """
    
    def __init__(self, db_path: str = "viral_engine.db"):
        self.db_path = db_path
        self.init_database()
        
        # Viral content patterns and frameworks
        self.viral_frameworks = {
            'challenge': {
                'template': "Join the {topic} challenge! Here's my take on it",
                'engagement_hooks': ['challenge', 'join us', 'your turn'],
                'virality_multiplier': 2.5
            },
            'transformation': {
                'template': "The amazing transformation using {topic}",
                'engagement_hooks': ['before/after', 'amazing results', 'transformation'],
                'virality_multiplier': 2.2
            },
            'behind_scenes': {
                'template': "Behind the scenes of {topic} - you won't believe this!",
                'engagement_hooks': ['behind scenes', 'exclusive', 'never seen'],
                'virality_multiplier': 1.8
            },
            'controversy': {
                'template': "The truth about {topic} that nobody talks about",
                'engagement_hooks': ['truth', 'secret', 'nobody knows'],
                'virality_multiplier': 2.1
            },
            'tutorial': {
                'template': "How to master {topic} in 60 seconds",
                'engagement_hooks': ['learn', 'master', 'quick tutorial'],
                'virality_multiplier': 1.6
            },
            'reaction': {
                'template': "My reaction to the {topic} trend - this is crazy!",
                'engagement_hooks': ['reaction', 'crazy', 'unbelievable'],
                'virality_multiplier': 1.9
            }
        }
        
        # Engagement triggers that boost virality
        self.viral_triggers = [
            'you won\'t believe', 'this changed everything', 'everyone is talking about',
            'going viral', 'trending now', 'must see', 'game changer', 'mind blown',
            'this is insane', 'wait for it', 'plot twist', 'unexpected', 'shocking'
        ]
        
        # Industry-specific trending sources
        self.trend_sources = {
            'general': ['google_trends', 'social_media_apis', 'news_apis'],
            'restaurant': ['food_trends', 'seasonal_menus', 'chef_challenges'],
            'fitness': ['workout_trends', 'health_challenges', 'transformation_stories'],
            'beauty': ['makeup_trends', 'skincare_routines', 'beauty_hacks'],
            'fashion': ['style_trends', 'outfit_challenges', 'fashion_weeks']
        }
    
    def init_database(self):
        """Initialize viral content database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trending topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_topics (
                topic_id TEXT PRIMARY KEY,
                topic_name TEXT NOT NULL,
                trend_score REAL,
                industry TEXT,
                keywords TEXT,
                hashtags TEXT,
                viral_elements TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                peak_period TEXT,
                engagement_potential REAL
            )
        ''')
        
        # Viral content templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viral_content (
                content_id TEXT PRIMARY KEY,
                topic_id TEXT,
                content_type TEXT,
                viral_prompt TEXT,
                viral_caption TEXT,
                viral_hashtags TEXT,
                engagement_hooks TEXT,
                optimal_posting_time TEXT,
                virality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES trending_topics (topic_id)
            )
        ''')
        
        # Viral campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viral_campaigns (
                campaign_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic_id TEXT,
                content_id TEXT,
                generated_assets TEXT,
                performance_prediction TEXT,
                actual_performance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES trending_topics (topic_id),
                FOREIGN KEY (content_id) REFERENCES viral_content (content_id)
            )
        ''')
        
        # Trend tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id TEXT,
                tracking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trend_score REAL,
                engagement_metrics TEXT,
                platform TEXT,
                FOREIGN KEY (topic_id) REFERENCES trending_topics (topic_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def detect_trending_topics(self, industry: str = 'general') -> List[TrendingTopic]:
        """Detect current trending topics for specific industry"""
        try:
            # This would integrate with real trend detection APIs
            # For demo, we'll simulate trending topics
            
            simulated_trends = await self._simulate_trending_topics(industry)
            
            # Store detected trends
            for trend in simulated_trends:
                await self._store_trending_topic(trend)
            
            print(f"✅ Detected {len(simulated_trends)} trending topics for {industry}")
            return simulated_trends
            
        except Exception as e:
            print(f"❌ Error detecting trending topics: {e}")
            return []
    
    async def _simulate_trending_topics(self, industry: str) -> List[TrendingTopic]:
        """Simulate trending topics (would be replaced with real API integration)"""
        
        industry_trends = {
            'restaurant': [
                {
                    'name': 'Plant-Based Protein Bowls',
                    'keywords': ['plant-based', 'protein', 'healthy', 'bowls', 'vegan'],
                    'hashtags': ['#PlantBased', '#ProteinBowl', '#HealthyEating', '#VeganLife'],
                    'viral_elements': ['health transformation', 'colorful presentation', 'before/after']
                },
                {
                    'name': 'Korean BBQ Fusion',
                    'keywords': ['korean', 'bbq', 'fusion', 'kimchi', 'spicy'],
                    'hashtags': ['#KoreanBBQ', '#FusionFood', '#Kimchi', '#SpicyFood'],
                    'viral_elements': ['cooking process', 'taste reactions', 'cultural fusion']
                }
            ],
            'fitness': [
                {
                    'name': '12-3-30 Treadmill Workout',
                    'keywords': ['treadmill', 'cardio', 'fat burning', '12-3-30', 'workout'],
                    'hashtags': ['#12330Challenge', '#TreadmillWorkout', '#CardioChallenge'],
                    'viral_elements': ['transformation results', 'workout demonstration', 'progress tracking']
                },
                {
                    'name': 'Pilates for Core Strength',
                    'keywords': ['pilates', 'core', 'strength', 'flexibility', 'mindful'],
                    'hashtags': ['#PilatesChallenge', '#CoreStrength', '#MindfulMovement'],
                    'viral_elements': ['graceful movements', 'core transformation', 'mindful practice']
                }
            ],
            'beauty': [
                {
                    'name': 'Glass Skin Routine',
                    'keywords': ['glass skin', 'skincare', 'dewy', 'korean beauty', 'glowing'],
                    'hashtags': ['#GlassSkin', '#SkincareRoutine', '#KBeauty', '#GlowUp'],
                    'viral_elements': ['before/after skin', 'routine steps', 'glowing results']
                }
            ],
            'general': [
                {
                    'name': 'Sustainable Living Hacks',
                    'keywords': ['sustainable', 'eco-friendly', 'zero waste', 'green living'],
                    'hashtags': ['#SustainableLiving', '#ZeroWaste', '#EcoFriendly', '#GreenLife'],
                    'viral_elements': ['easy swaps', 'environmental impact', 'cost savings']
                }
            ]
        }
        
        trends_data = industry_trends.get(industry, industry_trends['general'])
        trending_topics = []
        
        for i, trend_data in enumerate(trends_data):
            topic_id = f"{industry}_{i}_{int(datetime.now().timestamp())}"
            
            trend = TrendingTopic(
                topic_id=topic_id,
                topic_name=trend_data['name'],
                trend_score=random.uniform(75, 95),
                industry=industry,
                keywords=trend_data['keywords'],
                hashtags=trend_data['hashtags'],
                viral_elements=trend_data['viral_elements'],
                detected_at=datetime.now(),
                peak_period=self._predict_peak_period(),
                engagement_potential=random.uniform(80, 98)
            )
            
            trending_topics.append(trend)
        
        return trending_topics
    
    def _predict_peak_period(self) -> str:
        """Predict when trend will peak"""
        periods = ['next 2 hours', 'today evening', 'tomorrow morning', 'this weekend', 'next week']
        return random.choice(periods)
    
    async def _store_trending_topic(self, trend: TrendingTopic):
        """Store trending topic in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trending_topics
            (topic_id, topic_name, trend_score, industry, keywords, hashtags,
             viral_elements, peak_period, engagement_potential)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trend.topic_id, trend.topic_name, trend.trend_score, trend.industry,
            json.dumps(trend.keywords), json.dumps(trend.hashtags),
            json.dumps(trend.viral_elements), trend.peak_period,
            trend.engagement_potential
        ))
        
        conn.commit()
        conn.close()
    
    async def create_viral_content_from_trend(self, topic_id: str, framework: str = 'auto') -> ViralContent:
        """Create viral content based on trending topic"""
        try:
            # Get trending topic
            trend = await self._get_trending_topic(topic_id)
            if not trend:
                raise ValueError("Trending topic not found")
            
            # Select viral framework
            if framework == 'auto':
                framework = self._select_optimal_framework(trend)
            
            framework_data = self.viral_frameworks.get(framework, self.viral_frameworks['challenge'])
            
            # Generate viral content
            viral_prompt = await self._generate_viral_prompt(trend, framework_data)
            viral_caption = await self._generate_viral_caption(trend, framework_data)
            engagement_hooks = framework_data['engagement_hooks'] + [random.choice(self.viral_triggers)]
            
            # Calculate virality score
            virality_score = self._calculate_virality_score(trend, framework_data)
            
            # Determine optimal posting time
            optimal_time = self._determine_optimal_posting_time(trend)
            
            content_id = f"viral_{topic_id}_{framework}_{int(datetime.now().timestamp())}"
            
            viral_content = ViralContent(
                content_id=content_id,
                topic_id=topic_id,
                content_type='image',  # Default to image, can be customized
                viral_prompt=viral_prompt,
                viral_caption=viral_caption,
                viral_hashtags=trend.hashtags + [f'#{framework}Challenge'],
                engagement_hooks=engagement_hooks,
                optimal_posting_time=optimal_time,
                virality_score=virality_score
            )
            
            # Store viral content
            await self._store_viral_content(viral_content)
            
            return viral_content
            
        except Exception as e:
            print(f"❌ Error creating viral content: {e}")
            raise
    
    async def _get_trending_topic(self, topic_id: str) -> Optional[TrendingTopic]:
        """Get trending topic from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic_name, trend_score, industry, keywords, hashtags,
                   viral_elements, peak_period, engagement_potential
            FROM trending_topics WHERE topic_id = ?
        ''', (topic_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return TrendingTopic(
                topic_id=topic_id,
                topic_name=result[0],
                trend_score=result[1],
                industry=result[2],
                keywords=json.loads(result[3]),
                hashtags=json.loads(result[4]),
                viral_elements=json.loads(result[5]),
                detected_at=datetime.now(),
                peak_period=result[6],
                engagement_potential=result[7]
            )
        return None
    
    def _select_optimal_framework(self, trend: TrendingTopic) -> str:
        """Select best viral framework for trending topic"""
        # Analyze trend characteristics
        if 'transformation' in trend.viral_elements or 'before/after' in trend.viral_elements:
            return 'transformation'
        elif 'challenge' in trend.topic_name.lower() or trend.engagement_potential > 90:
            return 'challenge'
        elif 'tutorial' in trend.viral_elements or 'learn' in trend.keywords:
            return 'tutorial'
        elif trend.trend_score > 90:
            return 'controversy'
        else:
            return random.choice(['reaction', 'behind_scenes', 'challenge'])
    
    async def _generate_viral_prompt(self, trend: TrendingTopic, framework: Dict[str, Any]) -> str:
        """Generate AI prompt for viral content creation"""
        base_prompt = f"Viral social media content featuring {trend.topic_name}"
        
        # Add industry-specific elements
        if trend.industry == 'restaurant':
            base_prompt += ", mouth-watering food photography"
        elif trend.industry == 'fitness':
            base_prompt += ", energetic workout demonstration"
        elif trend.industry == 'beauty':
            base_prompt += ", stunning beauty transformation"
        
        # Add viral elements
        if 'transformation' in trend.viral_elements:
            base_prompt += ", dramatic before/after comparison"
        elif 'demonstration' in trend.viral_elements:
            base_prompt += ", step-by-step process demonstration"
        
        # Add trending keywords
        trending_elements = ', '.join(trend.keywords[:3])
        base_prompt += f", incorporating trending elements: {trending_elements}"
        
        base_prompt += ", hyperrealistic poster style, high engagement visual design, viral-optimized composition"
        
        return base_prompt
    
    async def _generate_viral_caption(self, trend: TrendingTopic, framework: Dict[str, Any]) -> str:
        """Generate viral-optimized caption"""
        # Start with viral hook
        viral_hooks = [
            f"🚨 The {trend.topic_name} trend is EVERYWHERE!",
            f"⚡ Why {trend.topic_name} is breaking the internet:",
            f"🔥 I tried the {trend.topic_name} trend and...",
            f"💥 {trend.topic_name} is the trend we've all been waiting for!"
        ]
        
        caption_parts = [random.choice(viral_hooks)]
        
        # Add framework-specific content
        framework_template = framework['template'].replace('{topic}', trend.topic_name)
        caption_parts.append(framework_template)
        
        # Add engagement trigger
        triggers = [
            "You won't believe what happened next! 👀",
            "The results will shock you! 😱",
            "This changed EVERYTHING! ✨",
            "Wait until you see this! 🤯"
        ]
        caption_parts.append(random.choice(triggers))
        
        # Add call to action
        cta_options = [
            "Double tap if you're trying this! 💕",
            "Tag someone who needs to see this! 👇",
            "Save this for later! 🔖",
            "What's your take on this trend? Comment below! 💬"
        ]
        caption_parts.append(random.choice(cta_options))
        
        # Add hashtags
        hashtag_string = ' '.join(trend.hashtags[:8])  # Limit to 8 hashtags
        caption_parts.append(hashtag_string)
        
        return '\n\n'.join(caption_parts)
    
    def _calculate_virality_score(self, trend: TrendingTopic, framework: Dict[str, Any]) -> float:
        """Calculate predicted virality score"""
        base_score = trend.trend_score * 0.4 + trend.engagement_potential * 0.6
        framework_bonus = framework['virality_multiplier'] * 10
        
        # Timing bonus
        if 'next 2 hours' in trend.peak_period or 'today' in trend.peak_period:
            timing_bonus = 15
        else:
            timing_bonus = 5
        
        # Industry bonus
        industry_multipliers = {'beauty': 1.2, 'fitness': 1.1, 'food': 1.15, 'general': 1.0}
        industry_bonus = industry_multipliers.get(trend.industry, 1.0) * 10
        
        total_score = base_score + framework_bonus + timing_bonus + industry_bonus
        return min(100, total_score)
    
    def _determine_optimal_posting_time(self, trend: TrendingTopic) -> str:
        """Determine optimal posting time for maximum virality"""
        time_strategies = {
            'fitness': ['6:00 AM', '12:00 PM', '6:00 PM'],
            'beauty': ['7:00 PM', '9:00 PM', '11:00 AM'],
            'restaurant': ['11:30 AM', '5:30 PM', '7:00 PM'],
            'general': ['9:00 AM', '1:00 PM', '7:00 PM']
        }
        
        optimal_times = time_strategies.get(trend.industry, time_strategies['general'])
        
        # Factor in peak period
        if 'morning' in trend.peak_period:
            return optimal_times[0]
        elif 'evening' in trend.peak_period:
            return optimal_times[2]
        else:
            return optimal_times[1]
    
    async def _store_viral_content(self, content: ViralContent):
        """Store viral content in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO viral_content
            (content_id, topic_id, content_type, viral_prompt, viral_caption,
             viral_hashtags, engagement_hooks, optimal_posting_time, virality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content.content_id, content.topic_id, content.content_type,
            content.viral_prompt, content.viral_caption,
            json.dumps(content.viral_hashtags), json.dumps(content.engagement_hooks),
            content.optimal_posting_time, content.virality_score
        ))
        
        conn.commit()
        conn.close()
    
    async def generate_viral_campaign(self, user_id: str, industry: str = 'general') -> ViralCampaign:
        """Generate complete viral campaign from trending topics"""
        try:
            # Detect trending topics
            trending_topics = await self.detect_trending_topics(industry)
            
            if not trending_topics:
                raise ValueError("No trending topics found")
            
            # Select highest scoring trend
            best_trend = max(trending_topics, key=lambda x: x.trend_score)
            
            # Create viral content
            viral_content = await self.create_viral_content_from_trend(best_trend.topic_id)
            
            # Generate AI assets
            print(f"🎨 Generating viral content: {viral_content.viral_prompt}")
            generated_image = await image_creator(viral_content.viral_prompt, "viral social media content")
            
            generated_assets = [generated_image] if generated_image else []
            
            # Predict performance
            performance_prediction = self._predict_viral_performance(viral_content, best_trend)
            
            campaign_id = f"viral_campaign_{user_id}_{int(datetime.now().timestamp())}"
            
            viral_campaign = ViralCampaign(
                campaign_id=campaign_id,
                user_id=user_id,
                trending_topic=best_trend,
                viral_content=viral_content,
                generated_assets=generated_assets,
                performance_prediction=performance_prediction,
                created_at=datetime.now()
            )
            
            # Store campaign
            await self._store_viral_campaign(viral_campaign)
            
            return viral_campaign
            
        except Exception as e:
            print(f"❌ Error generating viral campaign: {e}")
            raise
    
    def _predict_viral_performance(self, content: ViralContent, trend: TrendingTopic) -> Dict[str, float]:
        """Predict viral campaign performance"""
        base_engagement = content.virality_score / 100
        
        return {
            'predicted_reach': base_engagement * 10000,  # Estimated reach
            'predicted_engagement_rate': base_engagement * 0.08,  # 8% max engagement rate
            'predicted_shares': base_engagement * 500,  # Estimated shares
            'predicted_comments': base_engagement * 200,  # Estimated comments
            'virality_potential': content.virality_score,
            'trending_alignment': trend.trend_score
        }
    
    async def _store_viral_campaign(self, campaign: ViralCampaign):
        """Store viral campaign in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO viral_campaigns
            (campaign_id, user_id, topic_id, content_id, generated_assets, performance_prediction)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            campaign.campaign_id, campaign.user_id, campaign.trending_topic.topic_id,
            campaign.viral_content.content_id, json.dumps(campaign.generated_assets),
            json.dumps(campaign.performance_prediction)
        ))
        
        conn.commit()
        conn.close()
    
    async def get_viral_opportunities(self, industry: str = 'general') -> List[Dict[str, Any]]:
        """Get current viral opportunities for industry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT topic_id, topic_name, trend_score, peak_period, engagement_potential
                FROM trending_topics 
                WHERE industry = ? AND detected_at >= datetime('now', '-24 hours')
                ORDER BY trend_score DESC
                LIMIT 10
            ''', (industry,))
            
            results = cursor.fetchall()
            conn.close()
            
            opportunities = []
            for row in results:
                opportunities.append({
                    'topic_id': row[0],
                    'topic_name': row[1],
                    'trend_score': row[2],
                    'peak_period': row[3],
                    'engagement_potential': row[4],
                    'urgency_level': self._calculate_urgency(row[3], row[2])
                })
            
            return opportunities
            
        except Exception as e:
            print(f"❌ Error getting viral opportunities: {e}")
            return []
    
    def _calculate_urgency(self, peak_period: str, trend_score: float) -> str:
        """Calculate urgency level for trending topic"""
        if 'next 2 hours' in peak_period and trend_score > 90:
            return 'URGENT'
        elif 'today' in peak_period and trend_score > 80:
            return 'HIGH'
        elif trend_score > 75:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    async def create_trend_based_series(self, user_id: str, trend_topic_id: str, series_count: int = 5) -> List[ViralContent]:
        """Create series of viral content based on single trending topic"""
        try:
            trend = await self._get_trending_topic(trend_topic_id)
            if not trend:
                raise ValueError("Trending topic not found")
            
            viral_series = []
            frameworks = list(self.viral_frameworks.keys())
            
            for i in range(series_count):
                # Use different framework for each piece
                framework = frameworks[i % len(frameworks)]
                
                viral_content = await self.create_viral_content_from_trend(trend_topic_id, framework)
                
                # Customize for series
                viral_content.viral_caption += f" (Part {i+1}/{series_count})"
                viral_content.content_id += f"_series_{i+1}"
                
                viral_series.append(viral_content)
            
            return viral_series
            
        except Exception as e:
            print(f"❌ Error creating viral series: {e}")
            return []

# Helper functions for easy integration
async def detect_trends(industry: str = 'general'):
    """Quick trend detection"""
    engine = ViralContentEngine()
    return await engine.detect_trending_topics(industry)

async def create_viral_campaign(user_id: str, industry: str = 'general'):
    """Quick viral campaign creation"""
    engine = ViralContentEngine()
    return await engine.generate_viral_campaign(user_id, industry)

async def get_opportunities(industry: str = 'general'):
    """Quick viral opportunities"""
    engine = ViralContentEngine()
    return await engine.get_viral_opportunities(industry)

async def create_trend_content(topic_id: str, framework: str = 'auto'):
    """Quick viral content from trend"""
    engine = ViralContentEngine()
    return await engine.create_viral_content_from_trend(topic_id, framework)

async def main():
    """Test the viral content engine"""
    print("🔥 Viral Content & Trending Engine")
    print("=" * 40)
    
    engine = ViralContentEngine()
    
    # Demo: Detect trending topics
    print("🔍 Detecting trending topics for fitness industry...")
    trends = await engine.detect_trending_topics('fitness')
    
    for trend in trends:
        print(f"  📈 {trend.topic_name} (Score: {trend.trend_score:.1f})")
        print(f"     Keywords: {', '.join(trend.keywords[:3])}")
        print(f"     Peak: {trend.peak_period}")
    
    # Demo: Create viral campaign
    if trends:
        print(f"\n🚀 Creating viral campaign...")
        campaign = await engine.generate_viral_campaign('user_123', 'fitness')
        
        print(f"✅ Campaign created: {campaign.campaign_id}")
        print(f"📊 Virality Score: {campaign.viral_content.virality_score:.1f}")
        print(f"🎯 Predicted Reach: {campaign.performance_prediction['predicted_reach']:,.0f}")
        print(f"⏰ Optimal Posting: {campaign.viral_content.optimal_posting_time}")
        
        print(f"\n📝 Viral Caption Preview:")
        print(campaign.viral_content.viral_caption[:200] + "...")
    
    # Demo: Get viral opportunities
    print(f"\n💎 Current viral opportunities:")
    opportunities = await engine.get_viral_opportunities('fitness')
    
    for opp in opportunities[:3]:
        print(f"  🔥 {opp['topic_name']} - {opp['urgency_level']} urgency")
        print(f"     Trend Score: {opp['trend_score']:.1f} | Peak: {opp['peak_period']}")

if __name__ == "__main__":
    asyncio.run(main())