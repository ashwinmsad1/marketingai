"""
Enhanced Viral Content & Trending Engine
Detects trending topics from real data sources and creates viral-optimized content automatically
Integrates Reddit API, Google Trends, web scraping, and Claude LLM for content curation
"""

import asyncio
import aiohttp
import logging
import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
import random
import re
from urllib.parse import urlencode, quote_plus

# Real data source imports
import praw  # Reddit API
from pytrends.request import TrendReq  # Google Trends
from bs4 import BeautifulSoup  # Web scraping

# Rate limiting and caching
from functools import wraps
import pickle

# Database imports
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.models import ViralTrend, Campaign, AIContent

# Import our AI agents
from backend.agents.photo_agent import image_creator

# Rate limiting decorator
def rate_limit(max_calls: int, time_window: int):
    """Rate limiting decorator to prevent API abuse"""
    def decorator(func):
        calls = []
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the time window
            while calls and calls[0] <= now - time_window:
                calls.pop(0)
            
            if len(calls) >= max_calls:
                sleep_time = time_window - (now - calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await wrapper(*args, **kwargs)
            
            calls.append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Data source classes
@dataclass
class TrendSource:
    """Base class for trend sources"""
    name: str
    reliability_score: float
    last_updated: datetime
    rate_limit_remaining: int
    data: Dict[str, Any]

@dataclass
class TrendingTopic:
    """Enhanced trending topic data structure with real data sources"""
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
    # Enhanced fields for real data (required)
    sources: List[str]  # Which APIs/sources detected this trend
    # Enhanced fields for real data (optional)
    geographic_data: Optional[Dict[str, Any]] = None
    sentiment_score: Optional[float] = None
    related_trends: Optional[List[str]] = None
    content_examples: Optional[List[Dict[str, Any]]] = None
    claude_analysis: Optional[Dict[str, Any]] = None

@dataclass
class ViralContent:
    """Enhanced viral content template data structure with Claude analysis"""
    content_id: str
    topic_id: str
    content_type: str  # 'image', 'video', 'carousel'
    viral_prompt: str
    viral_caption: str
    viral_hashtags: List[str]
    engagement_hooks: List[str]
    optimal_posting_time: str
    virality_score: float
    # Enhanced fields
    claude_refinement: Optional[Dict[str, Any]] = None
    content_safety_score: Optional[float] = None
    brand_alignment_score: Optional[float] = None

# Claude LLM Integration Classes
class ClaudeContentCurator:
    """Claude LLM integration for content curation and analysis"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @rate_limit(max_calls=50, time_window=60)  # 50 calls per minute
    async def analyze_trend_relevance(self, trend_data: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """Use Claude to analyze trend relevance and viral potential"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        prompt = f"""
        Analyze this trending topic for viral marketing potential in the {industry} industry:
        
        Topic: {trend_data.get('name', 'Unknown')}
        Keywords: {', '.join(trend_data.get('keywords', []))}
        Source Data: {json.dumps(trend_data, indent=2)}
        
        Please analyze and provide:
        1. Relevance score (0-100) for {industry} industry
        2. Viral potential assessment (0-100)
        3. Content safety evaluation (0-100, where 100 is safest)
        4. Recommended content frameworks
        5. Potential risks or concerns
        6. Suggested hashtags and keywords
        7. Optimal content angles
        
        Provide response in JSON format with these exact keys:
        {{
            "relevance_score": <number>,
            "viral_potential": <number>,
            "safety_score": <number>,
            "recommended_frameworks": [<strings>],
            "risks": [<strings>],
            "suggested_hashtags": [<strings>],
            "content_angles": [<strings>],
            "reasoning": "<explanation>"
        }}
        """
        
        try:
            headers = {
                'x-api-key': self.api_key,
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': self.model,
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['content'][0]['text']
                    
                    # Parse JSON response
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # Fallback: extract JSON-like structure
                        return self._parse_claude_response(content)
                else:
                    return self._fallback_analysis(trend_data, industry)
        
        except Exception as e:
            logging.error(f"Claude API error: {e}")
            return self._fallback_analysis(trend_data, industry)
    
    def _parse_claude_response(self, content: str) -> Dict[str, Any]:
        """Parse Claude response when JSON parsing fails"""
        # Simple fallback parsing
        return {
            "relevance_score": 75,
            "viral_potential": 70,
            "safety_score": 85,
            "recommended_frameworks": ["challenge", "tutorial"],
            "risks": ["none identified"],
            "suggested_hashtags": ["#trending"],
            "content_angles": ["educational", "entertaining"],
            "reasoning": "Fallback analysis due to parsing error"
        }
    
    def _fallback_analysis(self, trend_data: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """Fallback analysis when Claude API is unavailable"""
        return {
            "relevance_score": 65,
            "viral_potential": 60,
            "safety_score": 80,
            "recommended_frameworks": ["general"],
            "risks": ["API unavailable - manual review recommended"],
            "suggested_hashtags": ["#trending", f"#{industry}"],
            "content_angles": ["informational"],
            "reasoning": "Fallback analysis - Claude API unavailable"
        }
    
    @rate_limit(max_calls=30, time_window=60)  # 30 calls per minute  
    async def curate_content_caption(self, trend: TrendingTopic, framework: str) -> Dict[str, str]:
        """Use Claude to create and refine content captions"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        prompt = f"""
        Create an engaging, viral-optimized social media caption for:
        
        Trend: {trend.topic_name}
        Industry: {trend.industry}
        Framework: {framework}
        Keywords: {', '.join(trend.keywords)}
        
        Requirements:
        - Hook the audience in the first line
        - Include trending keywords naturally
        - Add a clear call-to-action
        - Use appropriate emojis (but not excessive)
        - Stay authentic and brand-safe
        - Optimize for engagement
        
        Provide two versions: one for Instagram/Facebook and one for short-form vertical content.
        
        Response format:
        {{
            "instagram_caption": "<caption>",
            "short_form_caption": "<caption>",
            "key_hashtags": ["hashtag1", "hashtag2"],
            "engagement_prediction": <score 0-100>
        }}
        """
        
        try:
            headers = {
                'x-api-key': self.api_key,
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': self.model,
                'max_tokens': 800,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['content'][0]['text']
                    
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return self._fallback_caption(trend, framework)
                else:
                    return self._fallback_caption(trend, framework)
        
        except Exception as e:
            logging.error(f"Claude caption generation error: {e}")
            return self._fallback_caption(trend, framework)
    
    def _fallback_caption(self, trend: TrendingTopic, framework: str) -> Dict[str, str]:
        """Fallback caption generation"""
        base_caption = f"🔥 {trend.topic_name} is trending right now! Here's my take on it. What do you think? 💭 #trending #{trend.industry}"
        
        return {
            "instagram_caption": base_caption,
            "short_form_caption": base_caption,
            "key_hashtags": trend.hashtags[:5],
            "engagement_prediction": 65
        }

# Real Data Source Integration Classes

class RedditTrendDetector:
    """Reddit API integration for trending topic detection"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or "ViralEngine:v1.0 (by /u/your_username)"
        self.reddit = None
        self._init_reddit()
    
    def _init_reddit(self):
        """Initialize Reddit API connection"""
        try:
            if self.client_id and self.client_secret:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
        except Exception as e:
            logging.error(f"Reddit initialization error: {e}")
            self.reddit = None
    
    @rate_limit(max_calls=60, time_window=60)  # Reddit allows 60 requests per minute
    async def get_trending_topics(self, industry: str = 'general', limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending topics from relevant subreddits"""
        if not self.reddit:
            return []
        
        # Industry-specific subreddit mapping
        industry_subreddits = {
            'general': ['trending', 'popular', 'news', 'todayilearned'],
            'fitness': ['fitness', 'bodybuilding', 'yoga', 'running', 'weightlifting'],
            'beauty': ['SkincareAddiction', 'MakeupAddiction', 'beauty', 'Hair'],
            'restaurant': ['food', 'FoodPorn', 'recipes', 'Cooking', 'chefknives'],
            'fashion': ['malefashionadvice', 'femalefashionadvice', 'streetwear', 'fashion'],
            'tech': ['technology', 'gadgets', 'apple', 'android', 'programming']
        }
        
        subreddits = industry_subreddits.get(industry, industry_subreddits['general'])
        trending_topics = []
        
        try:
            for subreddit_name in subreddits[:3]:  # Limit to 3 subreddits to avoid rate limits
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get hot posts from the subreddit
                    for submission in subreddit.hot(limit=limit//len(subreddits[:3])):
                        if not submission.stickied:  # Skip pinned posts
                            # Extract keywords from title and content
                            keywords = self._extract_keywords(submission.title)
                            
                            topic_data = {
                                'name': submission.title,
                                'url': f"https://reddit.com{submission.permalink}",
                                'score': submission.score,
                                'upvote_ratio': submission.upvote_ratio,
                                'num_comments': submission.num_comments,
                                'created_utc': datetime.fromtimestamp(submission.created_utc),
                                'subreddit': subreddit_name,
                                'keywords': keywords,
                                'content': submission.selftext[:500] if submission.selftext else '',
                                'source': 'reddit'
                            }
                            
                            trending_topics.append(topic_data)
                
                except Exception as e:
                    logging.error(f"Error fetching from r/{subreddit_name}: {e}")
                    continue
            
            # Sort by engagement score (combination of upvotes and comments)
            trending_topics.sort(key=lambda x: x['score'] * (x['num_comments'] + 1), reverse=True)
            return trending_topics[:limit]
        
        except Exception as e:
            logging.error(f"Reddit trending topics error: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from Reddit post titles"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cant', 'this', 'that', 'these', 'those'}
        
        # Clean text and split into words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        return keywords[:10]  # Return top 10 keywords

        
        # Clean text and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Count frequency and return most common
        keyword_freq = {}
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, freq in sorted_keywords[:15]]

class GoogleTrendsDetector:
    """Google Trends integration using pytrends"""
    
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    @rate_limit(max_calls=10, time_window=60)  # Conservative rate limiting for Google Trends
    async def get_trending_searches(self, geo: str = 'US', category: int = 0) -> List[Dict[str, Any]]:
        """Get trending searches from Google Trends"""
        try:
            # Get trending searches
            trending_searches = self.pytrends.trending_searches(pn=geo)
            
            trends_data = []
            if not trending_searches.empty:
                for trend in trending_searches[0][:10]:  # Top 10 trending searches
                    
                    # Get related queries for additional context
                    try:
                        self.pytrends.build_payload([trend], cat=category, timeframe='now 7-d', geo=geo)
                        related_queries = self.pytrends.related_queries()
                        
                        # Extract rising queries as keywords
                        keywords = [trend.lower()]
                        if trend in related_queries and related_queries[trend]['rising'] is not None:
                            rising = related_queries[trend]['rising']['query'].tolist()
                            keywords.extend([q.lower() for q in rising[:5]])
                        
                        trend_data = {
                            'name': trend,
                            'keywords': keywords,
                            'geo': geo,
                            'category': category,
                            'timeframe': '7 days',
                            'source': 'google_trends'
                        }
                        
                        trends_data.append(trend_data)
                        
                        # Add delay to avoid rate limiting
                        await asyncio.sleep(1)
                    
                    except Exception as e:
                        logging.error(f"Error getting related queries for {trend}: {e}")
                        # Still add the trend without related queries
                        trends_data.append({
                            'name': trend,
                            'keywords': [trend.lower()],
                            'geo': geo,
                            'category': category,
                            'source': 'google_trends'
                        })
            
            return trends_data
        
        except Exception as e:
            logging.error(f"Google Trends error: {e}")
            return []
    
    @rate_limit(max_calls=5, time_window=60)  # Very conservative for detailed queries
    async def get_interest_over_time(self, keywords: List[str], timeframe: str = 'today 3-m', geo: str = 'US') -> Dict[str, Any]:
        """Get interest over time for specific keywords"""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
            interest_data = self.pytrends.interest_over_time()
            
            if not interest_data.empty:
                # Calculate trend direction
                recent_avg = interest_data.tail(7).mean().mean()  # Last week average
                older_avg = interest_data.head(7).mean().mean()  # First week average
                
                trend_direction = 'rising' if recent_avg > older_avg else 'declining'
                
                return {
                    'keywords': keywords,
                    'peak_interest': float(interest_data.max().max()),
                    'current_interest': float(interest_data.tail(1).mean().mean()),
                    'trend_direction': trend_direction,
                    'data_points': len(interest_data),
                    'source': 'google_trends'
                }
            
            return {}
        
        except Exception as e:
            logging.error(f"Interest over time error: {e}")
            return {}

class WebScrapingDetector:
    """Web scraping for industry-specific trend detection"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @rate_limit(max_calls=20, time_window=60)  # Be respectful to websites
    async def scrape_industry_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Scrape industry-specific websites for trending topics"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Industry-specific websites to scrape
        industry_sites = {
            'fitness': [
                'https://www.bodybuilding.com/content/the-latest-fitness-trends.html',
                'https://www.shape.com/latest-fitness-trends'
            ],
            'beauty': [
                'https://www.allure.com/beauty-trends',
                'https://www.harpersbazaar.com/beauty/'
            ],
            'restaurant': [
                'https://www.foodandwine.com/news',
                'https://www.eater.com/food-trends'
            ],
            'fashion': [
                'https://www.vogue.com/fashion/trends',
                'https://www.harpersbazaar.com/fashion/trends/'
            ]
        }
        
        sites = industry_sites.get(industry, [])
        scraped_trends = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for site_url in sites:
            try:
                async with self.session.get(site_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract article titles, headlines, and trending content
                        trends = self._extract_trending_content(soup, site_url, industry)
                        scraped_trends.extend(trends)
                        
                        # Be respectful - add delay between requests
                        await asyncio.sleep(2)
                    
                    else:
                        logging.warning(f"Failed to scrape {site_url}: Status {response.status}")
            
            except Exception as e:
                logging.error(f"Scraping error for {site_url}: {e}")
                continue
        
        return scraped_trends[:15]  # Limit to 15 trends
    
    def _extract_trending_content(self, soup: BeautifulSoup, site_url: str, industry: str) -> List[Dict[str, Any]]:
        """Extract trending content from scraped HTML"""
        trends = []
        
        # Common selectors for articles and headlines
        selectors = [
            'h1', 'h2', 'h3',  # Headlines
            '.headline', '.title', '.article-title',  # Common class names
            '[class*="title"]', '[class*="headline"]',  # Partial class matches
            'article h1', 'article h2',  # Article headlines
        ]
        
        found_content = set()  # Avoid duplicates
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:20]:  # Limit per selector
                    text = element.get_text().strip()
                    
                    # Filter relevant content
                    if (len(text) > 20 and len(text) < 200 and 
                        text not in found_content and
                        not self._is_navigation_content(text)):
                        
                        # Extract keywords
                        keywords = self._extract_keywords_from_title(text)
                        
                        # Only include if we found relevant keywords
                        if keywords and len(keywords) > 2:
                            trend_data = {
                                'name': text,
                                'keywords': keywords,
                                'source_url': site_url,
                                'industry': industry,
                                'source': 'web_scraping',
                                'scraped_at': datetime.now()
                            }
                            
                            trends.append(trend_data)
                            found_content.add(text)
            
            except Exception as e:
                logging.error(f"Error with selector {selector}: {e}")
                continue
        
        return trends
    
    def _is_navigation_content(self, text: str) -> bool:
        """Filter out navigation and non-content text"""
        nav_keywords = ['menu', 'navigation', 'footer', 'header', 'subscribe', 'newsletter', 'follow us', 'contact', 'about us', 'privacy policy', 'terms']
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in nav_keywords)
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract keywords from article titles"""
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'why', 'when', 'where', 'this', 'that', 'these', 'those', 'will', 'best', 'top', 'new', 'latest'}
        
        # Clean and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        return keywords[:8]  # Return top 8 keywords

@dataclass
class ViralCampaign:
    """Complete viral campaign data structure with enhanced real data"""
    campaign_id: str
    user_id: str
    trending_topic: TrendingTopic
    viral_content: ViralContent
    generated_assets: List[str]
    performance_prediction: Dict[str, float]
    created_at: datetime
    # Enhanced fields
    data_sources_used: Optional[List[str]] = None
    target_audience_insights: Optional[Dict[str, Any]] = None

class ViralContentEngine:
    """
    Enhanced AI-powered system for detecting trends and creating viral content
    Now integrates real data sources: Reddit, Google Trends, Web Scraping, and Claude LLM
    """
    
    def __init__(self):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # API keys for trend detection (enhanced)
        self.api_keys = {
            'reddit_client_id': os.getenv('REDDIT_CLIENT_ID'),
            'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'google': os.getenv('GOOGLE_API_KEY'),  # Keep legacy for other uses
            'newsapi': os.getenv('NEWS_API_KEY')  # Keep legacy for other uses
        }
        
        # Initialize real data source integrations
        self.reddit_detector = RedditTrendDetector(
            client_id=self.api_keys['reddit_client_id'],
            client_secret=self.api_keys['reddit_client_secret']
        )
        self.google_trends_detector = GoogleTrendsDetector()
        self.claude_curator = None  # Will be initialized when needed
        
        # Caching for performance
        self.trend_cache = {}
        self.cache_ttl = 1800  # 30 minutes cache TTL
        
        # Data source weights (for scoring)
        self.source_weights = {
            'reddit': 0.4,
            'google_trends': 0.3,
            'web_scraping': 0.3
        }
        
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
    
    def get_database_session(self) -> Session:
        """Get database session for PostgreSQL operations"""
        return next(get_db())
    
    async def detect_trending_topics(self, industry: str = 'general', use_cache: bool = True) -> List[TrendingTopic]:
        """Enhanced trending topic detection using real data sources"""
        try:
            # Check cache first
            cache_key = f"trends_{industry}_{datetime.now().hour}"  # Hourly cache
            if use_cache and cache_key in self.trend_cache:
                cache_data = self.trend_cache[cache_key]
                if (datetime.now() - cache_data['timestamp']).seconds < self.cache_ttl:
                    self.logger.info(f"Using cached trends for {industry}")
                    return cache_data['trends']
            
            self.logger.info(f"Fetching real trending topics for {industry} industry...")
            
            # Collect data from all sources concurrently
            tasks = []
            
            # Reddit trends
            tasks.append(self._fetch_reddit_trends(industry))
            
            
            # Google Trends
            tasks.append(self._fetch_google_trends(industry))
            
            # Web scraping
            tasks.append(self._fetch_web_scraping_trends(industry))
            
            # Execute all data collection tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process and merge results
            all_trend_data = []
            sources_used = []
            
            for i, result in enumerate(results):
                source_names = ['reddit', 'google_trends', 'web_scraping']
                if not isinstance(result, Exception) and result:
                    all_trend_data.extend(result)
                    sources_used.append(source_names[i])
                    self.logger.info(f"Successfully fetched {len(result)} trends from {source_names[i]}")
                elif isinstance(result, Exception):
                    self.logger.error(f"Error fetching from {source_names[i]}: {result}")
            
            # Convert raw data to TrendingTopic objects
            trending_topics = await self._process_raw_trends(all_trend_data, industry, sources_used)
            
            # Use Claude for curation and filtering
            if self.api_keys['anthropic']:
                trending_topics = await self._curate_with_claude(trending_topics, industry)
            
            # Store in cache
            if use_cache:
                self.trend_cache[cache_key] = {
                    'trends': trending_topics,
                    'timestamp': datetime.now()
                }
            
            # Store detected trends in database
            for trend in trending_topics:
                await self._store_trending_topic(trend)
            
            self.logger.info(f"Detected {len(trending_topics)} curated trending topics for {industry}")
            return trending_topics
            
        except Exception as e:
            self.logger.error(f"Error detecting trending topics: {e}")
            # Fallback to simulated data if all else fails
            return await self._simulate_trending_topics(industry)
    
    async def _fetch_reddit_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Fetch trending topics from Reddit"""
        try:
            return await self.reddit_detector.get_trending_topics(industry, limit=15)
        except Exception as e:
            self.logger.error(f"Reddit fetch error: {e}")
            return []
    
    
    async def _fetch_google_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Fetch trending searches from Google Trends"""
        try:
            return await self.google_trends_detector.get_trending_searches()
        except Exception as e:
            self.logger.error(f"Google Trends fetch error: {e}")
            return []
    
    async def _fetch_web_scraping_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Fetch trends via web scraping"""
        try:
            async with WebScrapingDetector() as scraper:
                return await scraper.scrape_industry_trends(industry)
        except Exception as e:
            self.logger.error(f"Web scraping fetch error: {e}")
            return []
    
    async def _process_raw_trends(self, raw_data: List[Dict[str, Any]], industry: str, sources: List[str]) -> List[TrendingTopic]:
        """Convert raw trend data into TrendingTopic objects with scoring"""
        trending_topics = []
        
        # Group similar trends and calculate composite scores
        trend_clusters = self._cluster_similar_trends(raw_data)
        
        for cluster in trend_clusters:
            try:
                # Calculate weighted score based on sources and engagement
                trend_score = self._calculate_composite_trend_score(cluster)
                
                # Determine most representative trend data
                primary_trend = max(cluster, key=lambda x: x.get('score', 0) or x.get('views', 0) or 0)
                
                # Extract and merge keywords
                all_keywords = []
                all_hashtags = []
                cluster_sources = []
                
                for trend_data in cluster:
                    all_keywords.extend(trend_data.get('keywords', []))
                    cluster_sources.append(trend_data.get('source', 'unknown'))
                    
                    # Generate hashtags from keywords
                    hashtags = [f"#{kw.replace(' ', '')}" for kw in trend_data.get('keywords', [])[:3]]
                    all_hashtags.extend(hashtags)
                
                # Deduplicate and limit
                unique_keywords = list(dict.fromkeys(all_keywords))[:10]
                unique_hashtags = list(dict.fromkeys(all_hashtags))[:8]
                unique_sources = list(dict.fromkeys(cluster_sources))
                
                # Create TrendingTopic object
                topic_id = f"{industry}_{hashlib.md5(primary_trend['name'].encode()).hexdigest()[:8]}_{int(datetime.now().timestamp())}"
                
                trending_topic = TrendingTopic(
                    topic_id=topic_id,
                    topic_name=primary_trend['name'][:100],  # Limit length
                    trend_score=trend_score,
                    industry=industry,
                    keywords=unique_keywords,
                    hashtags=unique_hashtags,
                    viral_elements=self._extract_viral_elements(cluster),
                    detected_at=datetime.now(),
                    peak_period=self._predict_peak_period(),
                    engagement_potential=min(trend_score * 1.2, 100),
                    sources=unique_sources,
                    geographic_data={'region': 'US'},  # Default for now
                    sentiment_score=self._estimate_sentiment(primary_trend),
                    related_trends=[],
                    content_examples=[trend_data for trend_data in cluster[:3]],  # Keep top 3 examples
                    claude_analysis=None  # Will be filled by Claude curation
                )
                
                trending_topics.append(trending_topic)
                
            except Exception as e:
                self.logger.error(f"Error processing trend cluster: {e}")
                continue
        
        # Sort by trend score
        trending_topics.sort(key=lambda x: x.trend_score, reverse=True)
        return trending_topics[:20]  # Limit to top 20
    
    def _cluster_similar_trends(self, raw_data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar trends together to avoid duplicates"""
        clusters = []
        processed = set()
        
        for trend in raw_data:
            if id(trend) in processed:
                continue
            
            # Create new cluster
            cluster = [trend]
            processed.add(id(trend))
            
            trend_keywords = set(word.lower() for word in trend.get('keywords', []))
            trend_name_words = set(trend['name'].lower().split())
            
            # Find similar trends
            for other_trend in raw_data:
                if id(other_trend) in processed:
                    continue
                
                other_keywords = set(word.lower() for word in other_trend.get('keywords', []))
                other_name_words = set(other_trend['name'].lower().split())
                
                # Calculate similarity
                keyword_similarity = len(trend_keywords & other_keywords) / len(trend_keywords | other_keywords) if trend_keywords | other_keywords else 0
                name_similarity = len(trend_name_words & other_name_words) / len(trend_name_words | other_name_words) if trend_name_words | other_name_words else 0
                
                # Group if similarity is high
                if keyword_similarity > 0.3 or name_similarity > 0.4:
                    cluster.append(other_trend)
                    processed.add(id(other_trend))
            
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_composite_trend_score(self, cluster: List[Dict[str, Any]]) -> float:
        """Calculate composite trend score from multiple data sources"""
        total_score = 0
        source_count = 0
        
        for trend_data in cluster:
            source = trend_data.get('source', 'unknown')
            weight = self.source_weights.get(source, 0.1)
            
            # Source-specific scoring
            if source == 'reddit':
                score = min((trend_data.get('score', 0) * trend_data.get('upvote_ratio', 0.5)) / 100, 100)
            elif source == 'google_trends':
                score = 80  # Google trends are inherently high value
            elif source == 'web_scraping':
                score = 60  # Web scraped content gets moderate score
            else:
                score = 50  # Default score
            
            total_score += score * weight
            source_count += weight
        
        # Normalize and add bonuses
        base_score = total_score / source_count if source_count > 0 else 50
        
        # Multi-source bonus
        unique_sources = len(set(trend.get('source') for trend in cluster))
        multi_source_bonus = min(unique_sources * 5, 15)
        
        final_score = min(base_score + multi_source_bonus, 100)
        return final_score
    
    def _extract_viral_elements(self, cluster: List[Dict[str, Any]]) -> List[str]:
        """Extract viral elements from trend cluster"""
        viral_elements = []
        
        for trend_data in cluster:
            # Check for viral indicators in content
            content = (trend_data.get('name', '') + ' ' + trend_data.get('description', '') + ' ' + ' '.join(trend_data.get('keywords', []))).lower()
            
            if any(word in content for word in ['challenge', 'try', 'attempt']):
                viral_elements.append('challenge')
            if any(word in content for word in ['before', 'after', 'transformation']):
                viral_elements.append('transformation')
            if any(word in content for word in ['tutorial', 'how to', 'learn', 'guide']):
                viral_elements.append('tutorial')
            if any(word in content for word in ['reaction', 'responds', 'reacts']):
                viral_elements.append('reaction')
            if any(word in content for word in ['behind', 'scenes', 'exclusive']):
                viral_elements.append('behind_scenes')
            if any(word in content for word in ['shocking', 'unbelievable', 'incredible']):
                viral_elements.append('shocking')
        
        return list(set(viral_elements)) or ['general']
    
    def _estimate_sentiment(self, trend_data: Dict[str, Any]) -> float:
        """Estimate sentiment score from trend data"""
        content = trend_data.get('name', '') + ' ' + trend_data.get('description', '')
        positive_words = ['amazing', 'best', 'love', 'great', 'awesome', 'incredible', 'fantastic']
        negative_words = ['worst', 'hate', 'terrible', 'awful', 'bad', 'horrible', 'disaster']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        if positive_count > negative_count:
            return 0.7
        elif negative_count > positive_count:
            return 0.3
        else:
            return 0.5  # Neutral
    
    async def _curate_with_claude(self, trends: List[TrendingTopic], industry: str) -> List[TrendingTopic]:
        """Use Claude to curate and filter trending topics"""
        if not self.claude_curator:
            self.claude_curator = ClaudeContentCurator(self.api_keys['anthropic'])
        
        curated_trends = []
        
        async with self.claude_curator:
            for trend in trends:
                try:
                    # Prepare trend data for Claude analysis
                    trend_data = {
                        'name': trend.topic_name,
                        'keywords': trend.keywords,
                        'sources': trend.sources,
                        'content_examples': trend.content_examples
                    }
                    
                    # Get Claude analysis
                    claude_analysis = await self.claude_curator.analyze_trend_relevance(trend_data, industry)
                    
                    # Filter based on Claude's assessment
                    if claude_analysis.get('safety_score', 0) >= 70 and claude_analysis.get('relevance_score', 0) >= 60:
                        # Update trend with Claude's analysis
                        trend.claude_analysis = claude_analysis
                        trend.trend_score = (trend.trend_score + claude_analysis.get('viral_potential', 50)) / 2
                        
                        # Update hashtags with Claude's suggestions
                        claude_hashtags = claude_analysis.get('suggested_hashtags', [])
                        trend.hashtags = list(set(trend.hashtags + claude_hashtags))[:10]
                        
                        curated_trends.append(trend)
                    
                    # Rate limit protection
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    self.logger.error(f"Error curating trend with Claude: {e}")
                    # Include trend anyway if Claude fails
                    curated_trends.append(trend)
        
        self.logger.info(f"Claude curated {len(curated_trends)} from {len(trends)} trends")
        return curated_trends
    
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
        try:
            db = self.get_database_session()
            
            # Create or update viral trend
            viral_trend = ViralTrend(
                id=trend.topic_id,
                topic=trend.topic_name,
                industry=trend.industry,
                platform='general',
                virality_score=trend.trend_score,
                engagement_rate=trend.engagement_potential,
                growth_rate=random.uniform(10, 50),  # Placeholder
                framework_type='general',
                key_elements=trend.viral_elements,
                recommended_hashtags=trend.hashtags,
                peak_time=datetime.now(),
                trend_lifespan=7,  # 7 days
                optimal_posting_times=['9:00', '12:00', '17:00', '21:00']
            )
            
            # Check if exists and update, otherwise create new
            existing = db.query(ViralTrend).filter(ViralTrend.id == trend.topic_id).first()
            if existing:
                for key, value in viral_trend.__dict__.items():
                    if key != '_sa_instance_state':
                        setattr(existing, key, value)
            else:
                db.add(viral_trend)
            
            db.commit()
            self.logger.info(f"Stored trending topic: {trend.topic_name}")
            
        except Exception as e:
            self.logger.error(f"Error storing trending topic: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def create_viral_content_from_trend(self, topic_id: str, framework: str = 'auto') -> ViralContent:
        """Enhanced viral content creation using Claude LLM and real trend data"""
        try:
            # Get trending topic
            trend = await self._get_trending_topic(topic_id)
            if not trend:
                raise ValueError("Trending topic not found")
            
            # Select viral framework (enhanced with Claude analysis)
            if framework == 'auto':
                framework = self._select_optimal_framework(trend)
                
                # Use Claude's recommended frameworks if available
                if trend.claude_analysis and trend.claude_analysis.get('recommended_frameworks'):
                    claude_frameworks = trend.claude_analysis['recommended_frameworks']
                    if claude_frameworks:
                        framework = claude_frameworks[0]  # Use top recommendation
            
            framework_data = self.viral_frameworks.get(framework, self.viral_frameworks['challenge'])
            
            # Initialize Claude curator if needed
            if not self.claude_curator and self.api_keys['anthropic']:
                self.claude_curator = ClaudeContentCurator(self.api_keys['anthropic'])
            
            # Generate enhanced viral content with Claude
            if self.claude_curator:
                async with self.claude_curator:
                    # Use Claude for caption generation
                    claude_caption_data = await self.claude_curator.curate_content_caption(trend, framework)
                    
                    viral_caption = claude_caption_data.get('instagram_caption', '')
                    claude_hashtags = claude_caption_data.get('key_hashtags', [])
                    engagement_prediction = claude_caption_data.get('engagement_prediction', 65)
            else:
                # Fallback to original method
                viral_caption = await self._generate_viral_caption(trend, framework_data)
                claude_hashtags = []
                engagement_prediction = 65
            
            # Generate enhanced viral prompt
            viral_prompt = await self._generate_enhanced_viral_prompt(trend, framework_data)
            
            # Combine engagement hooks
            engagement_hooks = framework_data['engagement_hooks'] + [random.choice(self.viral_triggers)]
            
            # Add Claude's content angles if available
            if trend.claude_analysis and trend.claude_analysis.get('content_angles'):
                engagement_hooks.extend(trend.claude_analysis['content_angles'][:2])
            
            # Calculate enhanced virality score
            virality_score = self._calculate_enhanced_virality_score(trend, framework_data, engagement_prediction)
            
            # Determine optimal posting time (enhanced with trend data)
            optimal_time = self._determine_enhanced_optimal_posting_time(trend)
            
            # Combine hashtags from multiple sources
            all_hashtags = list(set(
                trend.hashtags + 
                claude_hashtags + 
                [f'#{framework}Challenge'] +
                (trend.claude_analysis.get('suggested_hashtags', []) if trend.claude_analysis else [])
            ))[:15]  # Limit to 15 hashtags
            
            content_id = f"viral_{topic_id}_{framework}_{int(datetime.now().timestamp())}"
            
            viral_content = ViralContent(
                content_id=content_id,
                topic_id=topic_id,
                content_type='image',  # Default to image, can be customized
                viral_prompt=viral_prompt,
                viral_caption=viral_caption,
                viral_hashtags=all_hashtags,
                engagement_hooks=list(set(engagement_hooks))[:10],  # Dedupe and limit
                optimal_posting_time=optimal_time,
                virality_score=virality_score,
                # Enhanced fields
                claude_refinement=trend.claude_analysis,
                content_safety_score=trend.claude_analysis.get('safety_score', 80) if trend.claude_analysis else 80,
                brand_alignment_score=trend.claude_analysis.get('relevance_score', 70) if trend.claude_analysis else 70
            )
            
            # Store viral content
            await self._store_viral_content(viral_content)
            
            self.logger.info(f"Created enhanced viral content: {content_id} with score {virality_score:.1f}")
            return viral_content
            
        except Exception as e:
            self.logger.error(f"Error creating viral content: {e}")
            raise
    
    async def _generate_enhanced_viral_prompt(self, trend: TrendingTopic, framework: Dict[str, Any]) -> str:
        """Generate enhanced AI prompt using real trend data and sources"""
        base_prompt = f"Viral social media content featuring {trend.topic_name}"
        
        # Add source-specific context
        if 'reddit' in trend.sources:
            base_prompt += ", community-driven viral content"
        if 'google_trends' in trend.sources:
            base_prompt += ", trending search-optimized content"
        
        # Add industry-specific elements (enhanced)
        industry_prompts = {
            'restaurant': ", mouth-watering food photography, appetizing presentation, food styling",
            'fitness': ", energetic workout demonstration, motivation and transformation focus",
            'beauty': ", stunning beauty transformation, before/after comparison, professional makeup",
            'fashion': ", stylish fashion showcase, outfit coordination, trendy styling",
            'tech': ", sleek technology demonstration, modern gadgets, innovation focus"
        }
        
        base_prompt += industry_prompts.get(trend.industry, ", professional and engaging content")
        
        # Add viral elements from trend analysis
        if 'transformation' in trend.viral_elements:
            base_prompt += ", dramatic before/after comparison, transformation journey"
        elif 'challenge' in trend.viral_elements:
            base_prompt += ", challenge participation, step-by-step demonstration"
        elif 'tutorial' in trend.viral_elements:
            base_prompt += ", educational tutorial style, clear step-by-step process"
        
        # Add trending keywords for better relevance
        if trend.keywords:
            trending_elements = ', '.join(trend.keywords[:5])
            base_prompt += f", incorporating trending elements: {trending_elements}"
        
        # Add source examples context if available
        if trend.content_examples:
            example_keywords = []
            for example in trend.content_examples[:2]:
                example_keywords.extend(example.get('keywords', [])[:3])
            if example_keywords:
                unique_example_keywords = list(set(example_keywords))[:4]
                base_prompt += f", inspired by: {', '.join(unique_example_keywords)}"
        
        # Add Claude's content angles if available
        if trend.claude_analysis and trend.claude_analysis.get('content_angles'):
            angles = ', '.join(trend.claude_analysis['content_angles'][:3])
            base_prompt += f", content approach: {angles}"
        
        base_prompt += ", hyperrealistic poster style, high engagement visual design, viral-optimized composition, social media ready"
        
        return base_prompt
    
    def _calculate_enhanced_virality_score(self, trend: TrendingTopic, framework: Dict[str, Any], claude_prediction: float) -> float:
        """Enhanced virality score calculation with real data"""
        # Base score from trend data
        base_score = trend.trend_score * 0.3
        
        # Framework multiplier
        framework_bonus = framework['virality_multiplier'] * 8
        
        # Multi-source bonus
        source_bonus = len(trend.sources) * 5  # 5 points per unique source
        
        # Claude prediction bonus
        claude_bonus = (claude_prediction - 50) * 0.3  # Normalize Claude prediction
        
        # Sentiment bonus
        if trend.sentiment_score:
            if trend.sentiment_score > 0.6:  # Positive sentiment
                sentiment_bonus = 10
            elif trend.sentiment_score < 0.4:  # Negative sentiment (controversial can be viral)
                sentiment_bonus = 5
            else:
                sentiment_bonus = 0
        else:
            sentiment_bonus = 0
        
        # Timing bonus (enhanced)
        if 'next 2 hours' in trend.peak_period or 'today' in trend.peak_period:
            timing_bonus = 15
        elif 'tomorrow' in trend.peak_period:
            timing_bonus = 10
        else:
            timing_bonus = 5
        
        # Industry multiplier (enhanced)
        industry_multipliers = {
            'beauty': 1.3,
            'fitness': 1.25, 
            'fashion': 1.2,
            'restaurant': 1.2,
            'tech': 1.1,
            'general': 1.0
        }
        industry_bonus = industry_multipliers.get(trend.industry, 1.0) * 8
        
        # Content example quality bonus
        if trend.content_examples:
            high_engagement_examples = [ex for ex in trend.content_examples 
                                      if ex.get('score', 0) > 1000 or ex.get('views', 0) > 10000]
            example_bonus = len(high_engagement_examples) * 3
        else:
            example_bonus = 0
        
        # Calculate total score
        total_score = (base_score + framework_bonus + source_bonus + claude_bonus + 
                      sentiment_bonus + timing_bonus + industry_bonus + example_bonus)
        
        # Safety penalty if Claude identified risks
        if trend.claude_analysis and trend.claude_analysis.get('safety_score', 100) < 80:
            safety_penalty = (80 - trend.claude_analysis.get('safety_score', 80)) * 0.5
            total_score -= safety_penalty
        
        return min(100, max(10, total_score))  # Clamp between 10-100
    
    def _determine_enhanced_optimal_posting_time(self, trend: TrendingTopic) -> str:
        """Enhanced optimal posting time determination using trend data"""
        # Base industry strategies
        time_strategies = {
            'fitness': ['6:00 AM', '12:00 PM', '6:00 PM'],
            'beauty': ['7:00 PM', '9:00 PM', '11:00 AM'],
            'restaurant': ['11:30 AM', '5:30 PM', '7:00 PM'],
            'fashion': ['10:00 AM', '2:00 PM', '8:00 PM'],
            'tech': ['9:00 AM', '1:00 PM', '7:00 PM'],
            'general': ['9:00 AM', '1:00 PM', '7:00 PM']
        }
        
        optimal_times = time_strategies.get(trend.industry, time_strategies['general'])
        
        # Consider source data for timing
        if 'reddit' in trend.sources:
            # Reddit is most active during evening hours
            optimal_times = ['7:00 PM', '8:00 PM', '9:00 PM']
        
        # Factor in peak period from trend data
        if 'morning' in trend.peak_period:
            return optimal_times[0] if len(optimal_times) > 0 else '9:00 AM'
        elif 'evening' in trend.peak_period or 'night' in trend.peak_period:
            return optimal_times[-1] if len(optimal_times) > 0 else '7:00 PM'
        elif 'afternoon' in trend.peak_period:
            return optimal_times[1] if len(optimal_times) > 1 else '2:00 PM'
        else:
            return optimal_times[1] if len(optimal_times) > 1 else '1:00 PM'
    
    
    async def _get_trending_topic(self, topic_id: str) -> Optional[TrendingTopic]:
        """Get trending topic from database"""
        try:
            db = self.get_database_session()
            
            viral_trend = db.query(ViralTrend).filter(ViralTrend.id == topic_id).first()
            
            if viral_trend:
                return TrendingTopic(
                    topic_id=viral_trend.id,
                    topic_name=viral_trend.topic,
                    trend_score=viral_trend.virality_score or 0.0,
                    industry=viral_trend.industry or 'general',
                    keywords=viral_trend.key_elements or [],
                    hashtags=viral_trend.recommended_hashtags or [],
                    viral_elements=viral_trend.key_elements or [],
                    detected_at=viral_trend.created_at or datetime.now(),
                    peak_period=f"Peak in {viral_trend.trend_lifespan or 7} days",
                    engagement_potential=viral_trend.engagement_rate or 0.0
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting trending topic: {e}")
            return None
        finally:
            db.close()
    
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
        try:
            db = self.get_database_session()
            
            # Create AIContent entry for the viral content
            ai_content = AIContent(
                id=content.content_id,
                prompt=content.viral_prompt,
                content_type=content.content_type,
                platform_optimized=['facebook', 'instagram'],
                virality_score=content.virality_score,
                optimal_posting_time=content.optimal_posting_time,
                viral_elements=content.engagement_hooks
            )
            
            db.add(ai_content)
            db.commit()
            self.logger.info(f"Stored viral content: {content.content_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing viral content: {e}")
            db.rollback()
        finally:
            db.close()
    
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
            self.logger.info(f"Generating viral content: {viral_content.viral_prompt}")
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
            self.logger.error(f"Error generating viral campaign: {e}")
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
        try:
            db = self.get_database_session()
            
            # Create Campaign entry for the viral campaign
            campaign_record = Campaign(
                id=campaign.campaign_id,
                user_id=campaign.user_id,
                name=f"Viral Campaign: {campaign.trending_topic.topic_name}",
                type='viral',
                prompt=campaign.viral_content.viral_prompt,
                caption=campaign.viral_content.viral_caption,
                style='viral',
                industry=campaign.trending_topic.industry,
                status='draft'
            )
            
            db.add(campaign_record)
            db.commit()
            self.logger.info(f"Stored viral campaign: {campaign.campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing viral campaign: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def get_viral_opportunities(self, industry: str = 'general') -> List[Dict[str, Any]]:
        """Get current viral opportunities for industry"""
        try:
            db = self.get_database_session()
            
            # Query viral trends from last 24 hours
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            
            viral_trends = db.query(ViralTrend).filter(
                ViralTrend.industry == industry,
                ViralTrend.created_at >= yesterday
            ).order_by(ViralTrend.virality_score.desc()).limit(10).all()
            
            opportunities = []
            for trend in viral_trends:
                opportunities.append({
                    'topic_id': trend.id,
                    'topic_name': trend.topic,
                    'trend_score': trend.virality_score or 0,
                    'peak_period': f"Peak in {trend.trend_lifespan or 7} days",
                    'engagement_potential': trend.engagement_rate or 0,
                    'urgency_level': self._calculate_urgency(f"Peak in {trend.trend_lifespan or 7} days", trend.virality_score or 0)
                })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error getting viral opportunities: {e}")
            return []
        finally:
            db.close()
    
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
            self.logger.error(f"Error creating viral series: {e}")
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
    """Enhanced demo of the viral content engine with real data sources"""
    print("🔥 Enhanced Viral Content & Trending Engine")
    print("=" * 50)
    print("🚀 Now with Real Data Sources & Claude LLM!")
    print("=" * 50)
    
    engine = ViralContentEngine()
    
    # Check API configuration
    print("\n🔧 API Configuration Status:")
    apis = {
        'Reddit': engine.reddit_detector.reddit is not None,
        'Claude': engine.api_keys['anthropic'] is not None,
        'Google Trends': True,  # No API key needed
    }
    
    for api, status in apis.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api}: {'Configured' if status else 'Not configured'}")
    
    if not any(apis.values()):
        print("\n⚠️  No APIs configured! Using fallback simulated data.")
        print("   Set up API keys in .env file for real data sources.")
    
    print(f"\n🔍 Detecting REAL trending topics for fitness industry...")
    print("   Sources: Reddit + Google Trends + Web Scraping")
    
    # Detect trending topics with real data
    trends = await engine.detect_trending_topics('fitness')
    
    print(f"\n📊 Found {len(trends)} trending topics:")
    for i, trend in enumerate(trends[:5], 1):  # Show top 5
        print(f"\n  {i}. 📈 {trend.topic_name}")
        print(f"     🎯 Virality Score: {trend.trend_score:.1f}/100")
        print(f"     📱 Sources: {', '.join(trend.sources)}")
        print(f"     🏷️  Keywords: {', '.join(trend.keywords[:5])}")
        print(f"     ⏰ Peak Period: {trend.peak_period}")
        print(f"     😊 Sentiment: {trend.sentiment_score:.2f}" if trend.sentiment_score else "")
        
        # Show Claude analysis if available
        if trend.claude_analysis:
            claude = trend.claude_analysis
            print(f"     🤖 Claude Analysis:")
            print(f"        Safety Score: {claude.get('safety_score', 'N/A')}/100")
            print(f"        Relevance Score: {claude.get('relevance_score', 'N/A')}/100")
            print(f"        Recommended Frameworks: {', '.join(claude.get('recommended_frameworks', []))}")
    
    # Demo: Create enhanced viral content
    if trends:
        print(f"\n🚀 Creating enhanced viral content with Claude LLM...")
        trend = trends[0]  # Use top trend
        
        # Create viral content with Claude enhancement
        viral_content = await engine.create_viral_content_from_trend(
            trend.topic_id, 
            framework='auto'  # Let Claude choose optimal framework
        )
        
        print(f"\n✅ Enhanced Viral Content Created:")
        print(f"   🆔 Content ID: {viral_content.content_id}")
        print(f"   🎯 Virality Score: {viral_content.virality_score:.1f}/100")
        print(f"   🛡️  Safety Score: {viral_content.content_safety_score:.1f}/100")
        print(f"   🎨 Brand Alignment: {viral_content.brand_alignment_score:.1f}/100")
        print(f"   ⏰ Optimal Posting: {viral_content.optimal_posting_time}")
        print(f"   🏷️  Hashtags: {', '.join(viral_content.viral_hashtags[:8])}")
        
        print(f"\n📝 Claude-Generated Caption:")
        print(f"   {viral_content.viral_caption[:300]}...")
        
        print(f"\n🎨 Enhanced AI Prompt:")
        print(f"   {viral_content.viral_prompt[:200]}...")
        
    
    # Demo: Generate complete viral campaign
    if trends:
        print(f"\n🎬 Generating complete viral campaign...")
        campaign = await engine.generate_viral_campaign('demo_user', 'fitness')
        
        print(f"\n✅ Enhanced Viral Campaign Created:")
        print(f"   🆔 Campaign ID: {campaign.campaign_id}")
        print(f"   📊 Overall Virality Score: {campaign.viral_content.virality_score:.1f}/100")
        print(f"   🎯 Predicted Reach: {campaign.performance_prediction['predicted_reach']:,.0f}")
        print(f"   💰 Predicted ROI: {campaign.performance_prediction.get('predicted_roi', 0):.2f}%")
        print(f"   📱 Data Sources Used: {', '.join(campaign.trending_topic.sources)}")
        print(f"   🖼️  Generated Assets: {len(campaign.generated_assets)} files")
    
    # Demo: Get viral opportunities with urgency
    print(f"\n💎 Current viral opportunities (with urgency levels):")
    opportunities = await engine.get_viral_opportunities('fitness')
    
    urgent_count = len([opp for opp in opportunities if opp.get('urgency_level') == 'URGENT'])
    high_count = len([opp for opp in opportunities if opp.get('urgency_level') == 'HIGH'])
    
    print(f"   🚨 URGENT opportunities: {urgent_count}")
    print(f"   ⚡ HIGH priority opportunities: {high_count}")
    print(f"   📈 Total opportunities: {len(opportunities)}")
    
    for opp in opportunities[:3]:
        urgency_icon = {"URGENT": "🚨", "HIGH": "⚡", "MEDIUM": "⚠️", "LOW": "📊"}.get(opp.get('urgency_level', 'LOW'), '📊')
        print(f"\n   {urgency_icon} {opp['topic_name']}")
        print(f"      Trend Score: {opp['trend_score']:.1f} | Urgency: {opp.get('urgency_level', 'UNKNOWN')}")
        print(f"      {opp.get('peak_period', 'Peak timing unknown')}")
    
    # Show cache status
    print(f"\n📊 Performance Metrics:")
    print(f"   Cache entries: {len(engine.trend_cache)}")
    print(f"   Data source weights: Reddit({engine.source_weights['reddit']}) Google Trends({engine.source_weights['google_trends']}) Web Scraping({engine.source_weights['web_scraping']})")
    
    print(f"\n🎉 Demo completed! Check the generated content in your database.")
    print(f"💡 Tip: Configure API keys in .env for full real-data experience.")

if __name__ == "__main__":
    asyncio.run(main())