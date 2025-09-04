# Enhanced Viral Engine Setup & Usage Guide

## Overview

The Enhanced Viral Engine integrates **real data sources** to detect trending topics and uses **Claude LLM** for intelligent content curation. It replaces simulated data with actual trends from:

- **Reddit API** - Community discussions and viral content
- **YouTube Data API** - Trending videos and engagement metrics  
- **Google Trends** - Search trend analysis
- **Web Scraping** - Industry-specific trend sources
- **Claude LLM** - Content curation, safety filtering, and caption generation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup API Keys

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in your API keys in `.env` (see API Setup section below)

### 3. Basic Usage

```python
from viral_engine import ViralContentEngine

# Initialize the enhanced engine
engine = ViralContentEngine()

# Detect real trending topics for fitness industry
trends = await engine.detect_trending_topics('fitness')

# Create viral content from a specific trend
viral_content = await engine.create_viral_content_from_trend(trends[0].topic_id)

# Generate complete viral campaign
campaign = await engine.generate_viral_campaign('user_123', 'fitness')

print(f"Created viral campaign with {campaign.viral_content.virality_score:.1f} virality score")
print(f"Optimal posting time: {campaign.viral_content.optimal_posting_time}")
```

## API Setup Guide

### Required APIs

#### 1. Claude LLM API (Anthropic)
- **Purpose**: Content curation, safety filtering, caption generation
- **Signup**: https://console.anthropic.com/
- **Free Tier**: $5 free credits
- **Cost**: ~$0.003 per 1K tokens
- **Rate Limit**: 50 requests/minute

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### 2. Reddit API  
- **Purpose**: Trending topic detection from subreddits
- **Signup**: https://www.reddit.com/prefs/apps
- **Free**: Yes (60 requests/minute)
- **Setup**: Create "script" application

```env
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

#### 3. YouTube Data API
- **Purpose**: Trending video analysis
- **Signup**: https://console.developers.google.com/
- **Free Tier**: 10,000 quota units/day
- **Cost**: Additional quota available for purchase

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Optional APIs

#### Google Trends (pytrends)
- **Purpose**: Search trend analysis  
- **Free**: Yes (with rate limiting)
- **No API Key Required**: Uses unofficial pytrends library

#### Web Scraping
- **Purpose**: Industry-specific trend detection
- **Free**: Yes
- **Respectful**: Built-in delays and user-agent headers

## Features

### 🔥 Real Trend Detection

```python
# Multi-source trend detection
trends = await engine.detect_trending_topics('beauty')

for trend in trends:
    print(f"Trend: {trend.topic_name}")
    print(f"Sources: {', '.join(trend.sources)}")
    print(f"Virality Score: {trend.trend_score:.1f}")
    print(f"Keywords: {', '.join(trend.keywords[:5])}")
    print(f"Claude Analysis: {trend.claude_analysis}")
    print("---")
```

### 🤖 Claude-Enhanced Content Creation

```python
# Create content with Claude curation
viral_content = await engine.create_viral_content_from_trend(
    topic_id="trend_123", 
    framework="auto"  # Let Claude choose optimal framework
)

print(f"Generated Caption: {viral_content.viral_caption}")
print(f"Safety Score: {viral_content.content_safety_score}")
print(f"Brand Alignment: {viral_content.brand_alignment_score}")
print(f"Hashtags: {', '.join(viral_content.viral_hashtags)}")
```

### 📊 Industry-Specific Trends

```python
# Supported industries
industries = ['fitness', 'beauty', 'restaurant', 'fashion', 'tech', 'general']

for industry in industries:
    trends = await engine.detect_trending_topics(industry)
    print(f"{industry}: {len(trends)} trends detected")
```

### ⚡ Performance Features

- **Intelligent Caching**: 30-minute cache for trends
- **Rate Limiting**: Automatic API rate limit management
- **Fallback System**: Graceful degradation if APIs fail
- **Multi-Source Scoring**: Weighted scoring from multiple data sources

## Advanced Usage

### Custom Trend Analysis

```python
# Get viral opportunities with urgency levels
opportunities = await engine.get_viral_opportunities('fitness')

for opp in opportunities:
    if opp['urgency_level'] == 'URGENT':
        # Create content immediately for urgent trends
        content = await engine.create_viral_content_from_trend(opp['topic_id'])
        print(f"URGENT: Created content for {opp['topic_name']}")
```

### Trend Series Creation

```python
# Create a series of content from one trending topic
trend_id = trends[0].topic_id
content_series = await engine.create_trend_based_series(
    user_id='user_123',
    trend_topic_id=trend_id,
    series_count=5
)

print(f"Created {len(content_series)} pieces of content for the trend series")
```

### Content Safety & Brand Alignment

```python
# Filter content by safety and relevance scores
safe_trends = [
    trend for trend in trends 
    if trend.claude_analysis 
    and trend.claude_analysis.get('safety_score', 0) >= 80
    and trend.claude_analysis.get('relevance_score', 0) >= 70
]

print(f"Found {len(safe_trends)} high-quality, safe trends")
```

## Data Source Details

### Reddit Integration
- **Subreddits by Industry**: Automatically selects relevant subreddits
- **Engagement Scoring**: Uses upvotes, comments, and upvote ratio
- **Content Filtering**: Excludes pinned posts and low-quality content

### YouTube Integration  
- **Category Mapping**: Maps industries to YouTube categories
- **Engagement Metrics**: Views, likes, comments analysis
- **Trend Scoring**: Calculates engagement rate and viral potential

### Google Trends Integration
- **Real-time Trends**: Fetches current trending searches
- **Related Queries**: Expands keywords with related searches  
- **Geographic Data**: Supports region-specific trends

### Web Scraping
- **Industry Websites**: Scrapes authoritative industry publications
- **Respectful Scraping**: Built-in delays and proper headers
- **Content Extraction**: Smart extraction of headlines and articles

## Monitoring & Debugging

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# The engine will log:
# - API call successes/failures
# - Trend detection results
# - Claude curation outcomes
# - Rate limiting status
```

### Performance Monitoring

```python
# Check cache status
print(f"Cache entries: {len(engine.trend_cache)}")

# Monitor API usage
print(f"Reddit API initialized: {engine.reddit_detector.reddit is not None}")
print(f"YouTube API key configured: {engine.youtube_detector.api_key is not None}")
print(f"Claude API configured: {engine.api_keys['anthropic'] is not None}")
```

## Rate Limits & Costs

### Free Tier Limits (Per Day)
- **Reddit**: 8,640 requests (60/min × 1440 min)
- **YouTube**: ~400 trending video requests (25 videos × 4 categories × 4 regions)
- **Google Trends**: ~1,440 requests (10/min × 144 working minutes)
- **Claude**: ~1,667 requests with $5 free credits

### Estimated Monthly Costs
- **Claude**: $10-50 (depending on usage)
- **YouTube**: $0-20 (if exceeding free tier)
- **Reddit**: Free
- **Google Trends**: Free

## Troubleshooting

### Common Issues

1. **"Reddit initialization error"**
   - Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
   - Ensure Reddit app is configured as "script" type

2. **"YouTube API error: 403"**
   - Verify YOUTUBE_API_KEY is correct
   - Check quota limits in Google Console

3. **"Claude API error"**
   - Verify ANTHROPIC_API_KEY is valid
   - Check account has available credits

4. **"No trends detected"**
   - Check internet connection
   - Verify at least one API is working
   - Try different industry parameter

### Debug Mode

```python
# Enable detailed debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
trends_reddit = await engine._fetch_reddit_trends('fitness')
trends_youtube = await engine._fetch_youtube_trends('fitness')
trends_google = await engine._fetch_google_trends('fitness')

print(f"Reddit: {len(trends_reddit)} trends")
print(f"YouTube: {len(trends_youtube)} trends") 
print(f"Google: {len(trends_google)} trends")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from viral_engine import ViralContentEngine

app = FastAPI()
engine = ViralContentEngine()

@app.post("/detect-trends")
async def detect_trends(industry: str = "general"):
    trends = await engine.detect_trending_topics(industry)
    return {"trends": [asdict(trend) for trend in trends]}

@app.post("/create-viral-content")  
async def create_content(topic_id: str, framework: str = "auto"):
    content = await engine.create_viral_content_from_trend(topic_id, framework)
    return {"content": asdict(content)}
```

### Database Integration

The engine automatically stores trends and content in your PostgreSQL database using the existing models:
- `ViralTrend` - Stores detected trending topics
- `AIContent` - Stores generated viral content
- `Campaign` - Stores complete viral campaigns

## Security & Best Practices

### API Key Security
- Never commit API keys to version control
- Use environment variables (.env file)
- Rotate keys regularly
- Monitor API usage for anomalies

### Content Safety
- Claude automatically filters unsafe content
- Minimum safety score: 70/100
- Manual review recommended for sensitive industries
- Monitor generated content regularly

### Rate Limiting
- Built-in rate limiting for all APIs
- Automatic retry with exponential backoff
- Graceful degradation when limits exceeded
- Caching reduces API calls

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Test individual API components
4. Verify API keys and quotas
5. Check network connectivity

The Enhanced Viral Engine provides a robust, intelligent system for detecting real trends and creating high-quality viral content using cutting-edge AI technology.