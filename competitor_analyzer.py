"""
AI-Powered Competitor Analysis & Intelligence System
Analyzes competitor content and creates better versions using AI
"""

import asyncio
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import re
import hashlib
from urllib.parse import urlparse, urljoin

# Import our AI agents
from photo_agent import image_creator
from video_agent import video_from_prompt

@dataclass
class CompetitorContent:
    """Competitor content data structure"""
    content_id: str
    competitor_name: str
    platform: str
    content_type: str  # 'image', 'video', 'text'
    content_url: str
    caption: str
    engagement_metrics: Dict[str, int]
    analyzed_elements: Dict[str, Any]
    performance_score: float
    discovered_at: datetime

@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence insights"""
    competitor_name: str
    content_themes: List[str]
    top_performing_content: List[CompetitorContent]
    engagement_patterns: Dict[str, Any]
    content_gaps: List[str]
    recommended_actions: List[str]

@dataclass
class ImprovedContent:
    """AI-improved content based on competitor analysis"""
    original_content_id: str
    improvement_type: str
    new_prompt: str
    new_caption: str
    estimated_performance_lift: float
    competitive_advantages: List[str]

class CompetitorAnalysisEngine:
    """
    AI-powered system for analyzing competitors and creating superior content
    """
    
    def __init__(self, db_path: str = "competitor_analysis.db"):
        self.db_path = db_path
        self.init_database()
        
        # Content analysis patterns
        self.engagement_indicators = [
            'limited time', 'exclusive', 'new', 'sale', 'free', 'discount',
            'breakthrough', 'revolutionary', 'proven', 'guaranteed', 'secret',
            'discover', 'transform', 'amazing', 'incredible', 'must-have'
        ]
        
        # Performance multipliers for different content elements
        self.performance_factors = {
            'call_to_action': 1.3,
            'urgency_words': 1.4,
            'social_proof': 1.2,
            'emotional_triggers': 1.5,
            'visual_quality': 1.6,
            'clear_value_prop': 1.3
        }
    
    def init_database(self):
        """Initialize competitor analysis database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Competitor content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_content (
                content_id TEXT PRIMARY KEY,
                competitor_name TEXT NOT NULL,
                platform TEXT,
                content_type TEXT,
                content_url TEXT,
                caption TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                performance_score REAL,
                analyzed_elements TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Competitive intelligence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitive_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_name TEXT NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_themes TEXT,
                top_content_ids TEXT,
                engagement_patterns TEXT,
                recommended_actions TEXT
            )
        ''')
        
        # Improved content tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improved_content (
                improvement_id TEXT PRIMARY KEY,
                original_content_id TEXT,
                user_id TEXT,
                improvement_type TEXT,
                new_prompt TEXT,
                new_caption TEXT,
                generated_asset TEXT,
                estimated_lift REAL,
                actual_performance REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_content_id) REFERENCES competitor_content (content_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def analyze_competitor_url(self, competitor_url: str, competitor_name: str) -> Dict[str, Any]:
        """Analyze competitor content from URL"""
        try:
            # This would integrate with social media APIs for real data
            # For demo, we'll simulate analysis
            
            content_id = hashlib.md5(competitor_url.encode()).hexdigest()
            
            # Simulate content extraction
            simulated_content = {
                'caption': "🔥 New arrivals are here! Limited time offer - 50% off everything! Don't miss out on these amazing deals! Shop now before they're gone! #Sale #LimitedTime #ShopNow",
                'engagement': {'likes': 1247, 'comments': 89, 'shares': 156},
                'content_type': 'image',
                'platform': self._detect_platform(competitor_url)
            }
            
            # Analyze content elements
            analyzed_elements = await self._analyze_content_elements(simulated_content['caption'])
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(
                simulated_content['engagement'], 
                analyzed_elements
            )
            
            # Store in database
            competitor_content = CompetitorContent(
                content_id=content_id,
                competitor_name=competitor_name,
                platform=simulated_content['platform'],
                content_type=simulated_content['content_type'],
                content_url=competitor_url,
                caption=simulated_content['caption'],
                engagement_metrics=simulated_content['engagement'],
                analyzed_elements=analyzed_elements,
                performance_score=performance_score,
                discovered_at=datetime.now()
            )
            
            await self._store_competitor_content(competitor_content)
            
            return {
                'success': True,
                'content_id': content_id,
                'performance_score': performance_score,
                'analyzed_elements': analyzed_elements,
                'competitive_insights': await self._generate_insights_from_content(competitor_content)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing competitor URL: {e}")
            return {'success': False, 'error': str(e)}
    
    def _detect_platform(self, url: str) -> str:
        """Detect social media platform from URL"""
        domain = urlparse(url).netloc.lower()
        if 'facebook' in domain:
            return 'facebook'
        elif 'instagram' in domain:
            return 'instagram'
        elif 'twitter' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'linkedin' in domain:
            return 'linkedin'
        elif 'tiktok' in domain:
            return 'tiktok'
        else:
            return 'unknown'
    
    async def _analyze_content_elements(self, caption: str) -> Dict[str, Any]:
        """Analyze content elements for performance indicators"""
        elements = {
            'has_call_to_action': False,
            'urgency_words': [],
            'emotional_triggers': [],
            'hashtags': [],
            'emojis': [],
            'word_count': 0,
            'readability_score': 0,
            'sentiment': 'neutral'
        }
        
        # Extract hashtags
        elements['hashtags'] = re.findall(r'#\w+', caption)
        
        # Extract emojis (simplified)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+",
            flags=re.UNICODE
        )
        elements['emojis'] = emoji_pattern.findall(caption)
        
        # Check for call to action
        cta_words = ['shop', 'buy', 'order', 'call', 'visit', 'click', 'download', 'subscribe', 'sign up']
        elements['has_call_to_action'] = any(word in caption.lower() for word in cta_words)
        
        # Find urgency words
        urgency_words = ['limited', 'hurry', 'now', 'today', 'urgent', 'quick', 'fast', 'immediate']
        elements['urgency_words'] = [word for word in urgency_words if word in caption.lower()]
        
        # Emotional triggers
        emotional_words = ['amazing', 'incredible', 'exclusive', 'secret', 'breakthrough', 'revolutionary']
        elements['emotional_triggers'] = [word for word in emotional_words if word in caption.lower()]
        
        # Basic metrics
        elements['word_count'] = len(caption.split())
        elements['sentiment'] = await self._analyze_sentiment(caption)
        elements['readability_score'] = self._calculate_readability(caption)
        
        return elements
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (simplified)"""
        positive_words = ['amazing', 'great', 'awesome', 'fantastic', 'excellent', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate simple readability score"""
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?') + 1
        
        if len(words) == 0 or sentences == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / sentences
        avg_word_length = sum(len(word.strip('.,!?')) for word in words) / len(words)
        
        # Simple readability score (lower is more readable)
        readability = (avg_words_per_sentence * 0.39) + (avg_word_length * 11.8) - 15.59
        return max(0, min(100, readability))
    
    def _calculate_performance_score(self, engagement: Dict[str, int], elements: Dict[str, Any]) -> float:
        """Calculate content performance score"""
        # Base engagement score
        total_engagement = engagement.get('likes', 0) + engagement.get('comments', 0) + engagement.get('shares', 0)
        engagement_score = min(100, total_engagement / 10)  # Normalize to 0-100
        
        # Element multipliers
        multiplier = 1.0
        
        if elements['has_call_to_action']:
            multiplier *= self.performance_factors['call_to_action']
        
        if elements['urgency_words']:
            multiplier *= self.performance_factors['urgency_words']
        
        if elements['emotional_triggers']:
            multiplier *= self.performance_factors['emotional_triggers']
        
        if len(elements['hashtags']) > 0:
            multiplier *= 1.1
        
        if elements['sentiment'] == 'positive':
            multiplier *= 1.2
        
        return min(100, engagement_score * multiplier)
    
    async def _store_competitor_content(self, content: CompetitorContent):
        """Store competitor content in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO competitor_content
            (content_id, competitor_name, platform, content_type, content_url,
             caption, likes, comments, shares, performance_score, analyzed_elements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content.content_id, content.competitor_name, content.platform,
            content.content_type, content.content_url, content.caption,
            content.engagement_metrics.get('likes', 0),
            content.engagement_metrics.get('comments', 0),
            content.engagement_metrics.get('shares', 0),
            content.performance_score,
            json.dumps(content.analyzed_elements)
        ))
        
        conn.commit()
        conn.close()
    
    async def _generate_insights_from_content(self, content: CompetitorContent) -> Dict[str, Any]:
        """Generate competitive insights from single content piece"""
        return {
            'content_strengths': self._identify_content_strengths(content),
            'improvement_opportunities': self._identify_improvements(content),
            'estimated_performance': content.performance_score,
            'key_elements': content.analyzed_elements
        }
    
    def _identify_content_strengths(self, content: CompetitorContent) -> List[str]:
        """Identify what makes competitor content successful"""
        strengths = []
        elements = content.analyzed_elements
        
        if elements.get('has_call_to_action'):
            strengths.append("Clear call-to-action drives user action")
        
        if elements.get('urgency_words'):
            strengths.append(f"Creates urgency with words: {', '.join(elements['urgency_words'])}")
        
        if elements.get('emotional_triggers'):
            strengths.append(f"Uses emotional triggers: {', '.join(elements['emotional_triggers'])}")
        
        if len(elements.get('hashtags', [])) > 0:
            strengths.append(f"Good hashtag usage ({len(elements['hashtags'])} tags)")
        
        if elements.get('sentiment') == 'positive':
            strengths.append("Positive sentiment engages audience")
        
        if content.engagement_metrics.get('comments', 0) > 50:
            strengths.append("High comment engagement indicates strong audience connection")
        
        return strengths
    
    def _identify_improvements(self, content: CompetitorContent) -> List[str]:
        """Identify areas where we can improve on competitor content"""
        improvements = []
        elements = content.analyzed_elements
        
        if not elements.get('has_call_to_action'):
            improvements.append("Add stronger call-to-action to drive conversions")
        
        if not elements.get('urgency_words'):
            improvements.append("Create urgency with time-sensitive language")
        
        if len(elements.get('hashtags', [])) < 3:
            improvements.append("Increase hashtag usage for better discoverability")
        
        if elements.get('readability_score', 0) > 60:
            improvements.append("Simplify language for better readability")
        
        if elements.get('word_count', 0) > 50:
            improvements.append("Shorten caption for mobile-friendly consumption")
        
        if elements.get('sentiment') != 'positive':
            improvements.append("Add more positive language to increase engagement")
        
        return improvements
    
    async def create_improved_version(self, competitor_content_id: str, user_id: str) -> ImprovedContent:
        """Create AI-improved version of competitor content"""
        try:
            # Get competitor content
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT competitor_name, caption, analyzed_elements, performance_score
                FROM competitor_content WHERE content_id = ?
            ''', (competitor_content_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                raise ValueError("Competitor content not found")
            
            competitor_name, original_caption, elements_json, original_score = result
            elements = json.loads(elements_json)
            
            # Generate improved version
            improvements = self._identify_improvements({'analyzed_elements': elements})
            improved_prompt = await self._generate_improved_prompt(original_caption, improvements)
            improved_caption = await self._generate_improved_caption(original_caption, improvements)
            
            # Estimate performance lift
            estimated_lift = self._estimate_performance_lift(elements, improvements)
            
            # Create improved content object
            improvement_id = hashlib.md5(f"{competitor_content_id}_{user_id}_{datetime.now()}".encode()).hexdigest()
            
            improved_content = ImprovedContent(
                original_content_id=competitor_content_id,
                improvement_type="ai_enhanced",
                new_prompt=improved_prompt,
                new_caption=improved_caption,
                estimated_performance_lift=estimated_lift,
                competitive_advantages=improvements
            )
            
            # Store improvement
            await self._store_improved_content(improvement_id, improved_content, user_id)
            
            return improved_content
            
        except Exception as e:
            print(f"❌ Error creating improved version: {e}")
            raise
    
    async def _generate_improved_prompt(self, original_caption: str, improvements: List[str]) -> str:
        """Generate AI prompt for creating improved visual content"""
        # Extract key themes from original caption
        themes = self._extract_themes(original_caption)
        
        # Create enhanced prompt
        enhanced_prompt = f"Professional marketing image featuring {', '.join(themes[:3])}"
        
        # Add improvements
        if "urgency" in ' '.join(improvements).lower():
            enhanced_prompt += ", with urgent sale messaging and limited time offer visuals"
        
        if "emotional" in ' '.join(improvements).lower():
            enhanced_prompt += ", with emotional appeal and aspirational lifestyle elements"
        
        enhanced_prompt += ", hyperrealistic poster style, high-quality commercial photography"
        
        return enhanced_prompt
    
    async def _generate_improved_caption(self, original_caption: str, improvements: List[str]) -> str:
        """Generate improved caption based on analysis"""
        # Start with core message but improve structure
        improved_elements = []
        
        # Add attention-grabbing opening
        improved_elements.append("🚨 EXCLUSIVE OFFER:")
        
        # Extract main value proposition
        main_message = self._extract_main_message(original_caption)
        improved_elements.append(main_message)
        
        # Add improvements based on analysis
        if any("urgency" in imp.lower() for imp in improvements):
            improved_elements.append("⏰ Limited time only!")
        
        if any("call-to-action" in imp.lower() for imp in improvements):
            improved_elements.append("👆 Tap to shop now!")
        
        # Add social proof
        improved_elements.append("✨ Join thousands of satisfied customers!")
        
        # Add relevant hashtags
        hashtags = "#ExclusiveOffer #LimitedTime #ShopNow #CustomerFavorite #QualityGuaranteed"
        improved_elements.append(hashtags)
        
        return " ".join(improved_elements)
    
    def _extract_themes(self, caption: str) -> List[str]:
        """Extract main themes from caption"""
        # Simplified theme extraction
        words = caption.lower().replace('#', '').replace('@', '').split()
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
        meaningful_words = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Return most relevant themes
        return meaningful_words[:5]
    
    def _extract_main_message(self, caption: str) -> str:
        """Extract main marketing message"""
        sentences = caption.split('!')
        if sentences:
            return sentences[0].strip() + "!"
        return caption[:50] + "..."
    
    def _estimate_performance_lift(self, elements: Dict[str, Any], improvements: List[str]) -> float:
        """Estimate performance improvement percentage"""
        base_lift = 25.0  # Base improvement from AI optimization
        
        # Add lift for each improvement
        for improvement in improvements:
            if "call-to-action" in improvement.lower():
                base_lift += 15.0
            elif "urgency" in improvement.lower():
                base_lift += 20.0
            elif "emotional" in improvement.lower():
                base_lift += 18.0
            elif "hashtag" in improvement.lower():
                base_lift += 10.0
            elif "readability" in improvement.lower():
                base_lift += 12.0
        
        return min(100.0, base_lift)
    
    async def _store_improved_content(self, improvement_id: str, content: ImprovedContent, user_id: str):
        """Store improved content in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO improved_content
            (improvement_id, original_content_id, user_id, improvement_type,
             new_prompt, new_caption, estimated_lift)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            improvement_id, content.original_content_id, user_id,
            content.improvement_type, content.new_prompt, content.new_caption,
            content.estimated_performance_lift
        ))
        
        conn.commit()
        conn.close()
    
    async def generate_competitive_campaign(self, competitor_content_id: str, user_id: str) -> Dict[str, Any]:
        """Generate complete campaign that outperforms competitor"""
        try:
            # Create improved version
            improved_content = await self.create_improved_version(competitor_content_id, user_id)
            
            # Generate AI content using improved prompt
            print(f"🎨 Generating AI content with prompt: {improved_content.new_prompt}")
            generated_image = await image_creator(improved_content.new_prompt, "hyperrealistic marketing poster")
            
            if not generated_image:
                return {'success': False, 'error': 'Failed to generate AI content'}
            
            # Store generated asset
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE improved_content SET generated_asset = ?
                WHERE original_content_id = ? AND user_id = ?
            ''', (generated_image, competitor_content_id, user_id))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'generated_asset': generated_image,
                'improved_caption': improved_content.new_caption,
                'estimated_performance_lift': improved_content.estimated_performance_lift,
                'competitive_advantages': improved_content.competitive_advantages,
                'campaign_config': {
                    'content_path': generated_image,
                    'caption': improved_content.new_caption,
                    'improvement_type': improved_content.improvement_type
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating competitive campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_competitor_strategy(self, competitor_name: str) -> CompetitiveIntelligence:
        """Analyze overall competitor strategy"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all competitor content
            cursor.execute('''
                SELECT content_id, caption, performance_score, analyzed_elements
                FROM competitor_content 
                WHERE competitor_name = ?
                ORDER BY performance_score DESC
            ''', (competitor_name,))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return CompetitiveIntelligence(competitor_name, [], [], {}, [], [])
            
            # Analyze patterns
            top_performing = [
                CompetitorContent(
                    content_id=row[0],
                    competitor_name=competitor_name,
                    platform="",
                    content_type="",
                    content_url="",
                    caption=row[1],
                    engagement_metrics={},
                    analyzed_elements=json.loads(row[3]),
                    performance_score=row[2],
                    discovered_at=datetime.now()
                ) for row in results[:5]
            ]
            
            # Extract themes
            all_captions = [row[1] for row in results]
            content_themes = self._analyze_content_themes(all_captions)
            
            # Analyze engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(results)
            
            # Identify content gaps
            content_gaps = self._identify_content_gaps(results)
            
            # Generate recommendations
            recommendations = self._generate_strategic_recommendations(
                top_performing, content_themes, engagement_patterns
            )
            
            return CompetitiveIntelligence(
                competitor_name=competitor_name,
                content_themes=content_themes,
                top_performing_content=top_performing,
                engagement_patterns=engagement_patterns,
                content_gaps=content_gaps,
                recommended_actions=recommendations
            )
            
        except Exception as e:
            print(f"❌ Error analyzing competitor strategy: {e}")
            return CompetitiveIntelligence(competitor_name, [], [], {}, [], [str(e)])
    
    def _analyze_content_themes(self, captions: List[str]) -> List[str]:
        """Analyze common themes across competitor content"""
        all_words = []
        for caption in captions:
            words = caption.lower().replace('#', '').replace('@', '').split()
            all_words.extend(words)
        
        # Count word frequency
        word_count = {}
        for word in all_words:
            if len(word) > 3:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Return top themes
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10] if count > 1]
    
    def _analyze_engagement_patterns(self, results: List[Tuple]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        performance_scores = [row[2] for row in results]
        
        return {
            'avg_performance': sum(performance_scores) / len(performance_scores) if performance_scores else 0,
            'top_performance': max(performance_scores) if performance_scores else 0,
            'consistency_score': 100 - (max(performance_scores) - min(performance_scores)) if performance_scores else 0,
            'total_content_pieces': len(results)
        }
    
    def _identify_content_gaps(self, results: List[Tuple]) -> List[str]:
        """Identify gaps in competitor content strategy"""
        gaps = []
        
        # Analyze what's missing
        all_elements = []
        for row in results:
            elements = json.loads(row[3])
            all_elements.append(elements)
        
        # Check for missing elements across content
        cta_count = sum(1 for elem in all_elements if elem.get('has_call_to_action'))
        urgency_count = sum(1 for elem in all_elements if elem.get('urgency_words'))
        
        if cta_count < len(all_elements) * 0.5:
            gaps.append("Inconsistent call-to-action usage")
        
        if urgency_count < len(all_elements) * 0.3:
            gaps.append("Limited urgency creation")
        
        return gaps
    
    def _generate_strategic_recommendations(self, top_content: List[CompetitorContent], 
                                         themes: List[str], patterns: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        if patterns['avg_performance'] < 60:
            recommendations.append("Competitor shows vulnerability - create superior content versions")
        
        if themes:
            recommendations.append(f"Focus on these successful themes: {', '.join(themes[:3])}")
        
        if patterns['consistency_score'] < 70:
            recommendations.append("Competitor inconsistent - maintain quality advantage")
        
        recommendations.extend([
            "Create AI-enhanced versions of top-performing content",
            "Develop content series around successful themes",
            "Implement stronger calls-to-action than competitor",
            "Use performance data to optimize posting times"
        ])
        
        return recommendations

# Helper functions for easy integration
async def analyze_competitor(competitor_url: str, competitor_name: str):
    """Quick competitor analysis"""
    engine = CompetitorAnalysisEngine()
    return await engine.analyze_competitor_url(competitor_url, competitor_name)

async def create_better_campaign(competitor_content_id: str, user_id: str):
    """Quick campaign creation that beats competitor"""
    engine = CompetitorAnalysisEngine()
    return await engine.generate_competitive_campaign(competitor_content_id, user_id)

async def get_competitor_intel(competitor_name: str):
    """Quick competitive intelligence"""
    engine = CompetitorAnalysisEngine()
    return await engine.analyze_competitor_strategy(competitor_name)

async def main():
    """Test the competitor analysis system"""
    print("🕵️ AI-Powered Competitor Analysis System")
    print("=" * 50)
    
    engine = CompetitorAnalysisEngine()
    
    # Demo: Analyze competitor content
    competitor_url = "https://facebook.com/competitor-post"
    competitor_name = "Local Restaurant Competitor"
    
    print(f"🔍 Analyzing competitor content from {competitor_name}...")
    analysis_result = await engine.analyze_competitor_url(competitor_url, competitor_name)
    
    if analysis_result['success']:
        print(f"📊 Performance Score: {analysis_result['performance_score']:.1f}")
        print(f"🎯 Key Elements: {', '.join(analysis_result['analyzed_elements'].keys())}")
        
        # Demo: Create improved version
        content_id = analysis_result['content_id']
        user_id = "user_123"
        
        print(f"\n🚀 Creating improved campaign...")
        improved_campaign = await engine.generate_competitive_campaign(content_id, user_id)
        
        if improved_campaign['success']:
            print(f"✅ Generated improved content: {improved_campaign['generated_asset']}")
            print(f"📈 Estimated performance lift: {improved_campaign['estimated_performance_lift']:.1f}%")
            print(f"💪 Competitive advantages: {len(improved_campaign['competitive_advantages'])}")
        
        # Demo: Strategic analysis
        print(f"\n📋 Analyzing competitor strategy...")
        strategy = await engine.analyze_competitor_strategy(competitor_name)
        print(f"🎯 Content themes: {', '.join(strategy.content_themes[:5])}")
        print(f"📊 Avg performance: {strategy.engagement_patterns['avg_performance']:.1f}")
        print(f"💡 Recommendations: {len(strategy.recommended_actions)}")

if __name__ == "__main__":
    asyncio.run(main())