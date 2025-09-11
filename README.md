# 🚀 AI Marketing Automation Platform

> **Professional SaaS Application** for AI-powered marketing campaigns across Meta/Facebook platforms

A full-stack marketing automation platform that leverages multiple AI services to create, optimize, and manage marketing campaigns with special focus on the Indian market and Meta/Facebook advertising.

## 🎯 Platform Overview

- **Target Audience**: Indian businesses and entrepreneurs
- **Architecture**: FastAPI backend + React TypeScript frontend + PostgreSQL database
- **Approach**: User input-driven personalization (NO industry templates)
- **Payment**: UPI + Razorpay integration optimized for Indian market

## ✨ Key Features

### 🤖 AI Content Generation
- **Google Gemini 2.5 Flash** for hyperrealistic poster generation
- **Google Veo 3.0** for 8-second AI video creation
- **Dynamic content generation** with user context personalization
- **Multi-format support** (16:9, 1:1, 9:16 aspect ratios)

### 💳 Payment & Subscriptions
- **UPI Payment Integration** with QR codes and deep links
- **Razorpay** for subscription billing and invoice generation
- **Tier-based usage limits** with automatic enforcement
- **Indian currency support** (₹5,000, ₹25,000, ₹100,000/month)

### 📱 Meta Campaign Automation
- **Facebook & Instagram** cross-platform campaign management
- **OAuth user onboarding** for seamless account connection
- **Performance analytics** and real-time insights
- **Automated posting** and campaign optimization

### 🔥 Viral Content Engine
- **Real-time trend detection** from Reddit and Google Trends
- **Claude AI curation** for content safety and brand alignment
- **Multi-source scoring** for viral potential analysis
- **Automated hashtag generation** and optimal posting times

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/                    # FastAPI Application
│   ├── main.py            # Main application entry point
│   └── dependencies.py    # Authentication & database dependencies
├── core/                  # Core Functionality
│   ├── config.py         # Pydantic settings with validation
│   ├── security.py       # JWT, password hashing, API validation
│   └── exceptions.py     # Custom exception hierarchy
├── agents/               # AI Agents
│   ├── photo_agent.py    # Image generation agent
│   ├── video_agent.py    # Video generation agent (Google Veo 3.0)
│   └── facebook_agent.py # Social media automation
├── engines/              # Business Logic Engines
│   ├── marketing_automation.py    # Core marketing engine
│   ├── viral_engine.py          # Viral content generation
│   ├── personalization_engine.py # ML personalization algorithms
│   └── revenue_tracking.py      # ROI and attribution tracking
├── services/             # Service Layer
│   ├── personalization_service.py # User input personalization
│   ├── campaign_service.py       # Campaign management
│   ├── media_service.py         # Media generation service
│   ├── analytics_service.py     # Analytics and reporting
│   └── user_service.py          # User management
├── integrations/         # Third-party Integrations
│   ├── meta/            # Facebook/Instagram APIs
│   ├── payment/         # Razorpay (Indian market)
│   └── platform/        # Other social platforms
├── ml/                   # Machine Learning Components
│   ├── ab_testing/      # A/B testing framework with statistical analysis
│   ├── content_generation/ # Dynamic content generation
│   └── learning/        # Adaptive learning system
├── api/v1/              # Versioned API Endpoints
│   ├── auth.py         # Authentication endpoints
│   ├── campaigns.py    # Campaign management
│   ├── media.py        # AI media generation
│   └── personalization.py # Video & Image strategy APIs
├── auth/               # Authentication System
├── database/           # Database Layer
├── tests/              # Comprehensive Test Suite
│   ├── unit/          # Unit tests (framework core, statistical analysis)
│   ├── integration/   # Integration tests (end-to-end workflows)  
│   ├── performance/   # Performance & load tests
│   ├── api/           # API endpoint tests
│   ├── fixtures/      # Test data fixtures
│   └── utils/         # Test utilities and helpers
└── utils/             # Utilities and Helpers
```

### Frontend Structure  
- **src/pages/** - Main application pages/routes
- **src/components/** - Reusable UI components
- **src/design-system/** - Design system components and layouts
- **src/contexts/** - React contexts (AuthContext, etc.)
- **src/services/** - API service layer
- **src/types/** - TypeScript type definitions
- **src/utils/** - Utility functions and helpers

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.13+
- **PostgreSQL** 14+
- **Git**

### 1. Clone Repository
```bash
git clone <repository-url>
cd marketingai
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Setup database
createdb ai_marketing_platform

# Run migrations
alembic upgrade head

# Start backend server
python -m app.main
# OR
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Environment Configuration
Copy `.env.example` to `.env` and configure:

```bash
# Core API Keys
API_KEY=your_google_ai_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_marketing_platform

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-256-bits-minimum
EMAIL_SECRET_KEY=your-email-secret-key-change-in-production

# Payment Processing (Indian Market)
RAZORPAY_KEY_ID=rzp_live_your_key_id_here
RAZORPAY_KEY_SECRET=your_secret_key_here
UPI_MERCHANT_VPA=merchant@paytm

# Meta Integration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Email Service (Production)
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
```

## 💰 Subscription Plans

| Plan | Price | Campaigns | AI Generations | Features |
|------|-------|-----------|----------------|----------|
| **Starter** | ₹999/month | 5 | 100 | Basic AI content, Meta posting |
| **Professional** | ₹1,999/month | 25 | 500 | Advanced AI, Analytics, A/B testing |
| **Enterprise** | ₹2,999/month | Unlimited | Unlimited | Full platform access, Priority support |

## 🛠️ Development Commands

### Backend
```bash
cd backend

# Code formatting
black backend/

# Linting
flake8 backend/

# Run tests
pytest

# Run tests with coverage
pytest --cov=ml.ab_testing --cov=services --cov=api.v1 --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only
pytest -m api          # API tests only

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend
```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint-fix

# Build for production
npm run build
```

### Docker Development
```bash
# Run full stack
docker-compose up

# Run with rebuild
docker-compose up --build
```

## 📊 Database Schema

### Core Tables
- **users** - User accounts with subscription tiers
- **campaigns** - Marketing campaigns with status tracking
- **ai_content** - Generated content (images, videos, text)
- **conversions** - Performance tracking and attribution
- **personalization_profiles** - User behavior and preferences
- **viral_content** - Trending content analysis
- **meta_accounts** - Connected Facebook/Instagram accounts
- **payments** - Payment processing and billing history
- **billing_subscriptions** - Subscription management and usage tracking

### Performance Optimizations
- **Comprehensive indexing** on frequently queried columns
- **Composite indexes** for multi-column queries
- **Connection pooling** and query optimization
- **Background tasks** for heavy AI operations

## 🔐 Security Features

- **JWT Authentication** with 30-minute expiration
- **Email verification** required for critical features
- **Password hashing** using bcrypt
- **Rate limiting** and CORS protection
- **Input validation** using Pydantic models
- **SQL injection prevention** through SQLAlchemy ORM
- **API key rotation** support for all external services

## 🌐 Third-Party Integrations

### AI Services
- **Google AI (Gemini + Veo)** - Content generation
- **Claude AI** - Content curation and safety filtering

### Payment Processing
- **Razorpay** - UPI payments and subscription billing
- **UPI Integration** - QR codes and deep links for all major UPI apps

### Social Media
- **Meta Marketing API** - Facebook/Instagram campaign automation
- **OAuth Integration** - Seamless user account connection

### Trend Analysis
- **Reddit API** - Community discussions and viral content
- **Google Trends** - Real-time search trend analysis

### Infrastructure
- **PostgreSQL** - Primary database with optimized performance
- **SendGrid** - Production email delivery service
- **Docker** - Containerized deployment

## 🎨 Campaign Types

### Video Campaigns
- **AI Video Ads** with Google Veo 3.0 (8-second videos)
- **Cinematic & Commercial** styles
- **Multiple aspect ratios** (16:9, 1:1, 9:16)
- **User context personalization**

### Image Campaigns
- **Quick Campaign** - Rapid AI poster generation
- **Personalized Campaign** - Full ML personalization
- **Professional, Modern, Creative** styles
- **Format optimization** for different platforms

### Viral Campaigns
- **Real-time trending** content detection
- **Multi-source analysis** from Reddit and Google Trends
- **Claude AI curation** for safety and relevance
- **Automated hashtag** generation

## 📈 Analytics & Reporting

- **Real-time performance tracking** across all campaigns
- **ROI and attribution analysis** with revenue tracking
- **A/B testing framework** with statistical analysis and AI-powered recommendations
- **Viral content performance** scoring and insights
- **User engagement analytics** and behavior patterns
- **Subscription usage monitoring** and tier management

## 🚨 Production Deployment

### Pre-Launch Checklist
- ✅ Google AI API (paid tier recommended)
- ✅ Razorpay account verified and live
- ✅ UPI payments configured and tested
- ✅ SendGrid email service setup
- ⚠️ **Meta App Review completed** (CRITICAL - 7-14 days)
- ✅ PostgreSQL database with SSL
- ✅ Domain with SSL certificate
- ✅ All environment variables configured

### Performance Considerations
- **Database indexing** for optimal query performance
- **Redis caching** for viral content and trending data
- **CDN integration** for media hosting
- **Connection pooling** for database optimization
- **Background task queues** for AI processing

## 💡 User Input Personalization

**NO INDUSTRY TEMPLATES** - The platform uses user input-driven personalization:

### Required User Context
All personalized campaigns require:
- **Business Description** - What the business does specifically
- **Target Audience** - Detailed demographics and psychographics
- **Unique Value Proposition** - What makes the business unique

### Personalization APIs
- `POST /api/v1/personalization/video-strategy` - Generate personalized video campaigns
- `POST /api/v1/personalization/image-strategy` - Generate personalized image campaigns
- `POST /api/v1/personalization/profile` - Create user profiles
- `POST /api/v1/personalization/dashboard` - Personalized insights

### A/B Testing APIs
- `POST /api/v1/personalization/ab-tests` - Create A/B tests
- `GET /api/v1/personalization/ab-tests` - List user's A/B tests
- `POST /api/v1/personalization/ab-tests/{id}/start` - Start A/B test
- `GET /api/v1/personalization/ab-tests/{id}/results` - Get test results

## 🔧 API Documentation

### Authentication Endpoints
```bash
POST /api/auth/register          # User registration
POST /api/auth/login             # User login
POST /api/auth/verify-email      # Email verification
POST /api/auth/forgot-password   # Password reset
```

### Campaign Management
```bash
GET  /api/campaigns              # List user campaigns
POST /api/campaigns              # Create new campaign
GET  /api/campaigns/{id}         # Get campaign details
PUT  /api/campaigns/{id}         # Update campaign
```

### AI Content Generation
```bash
POST /api/media/generate-image   # Generate AI images
POST /api/media/generate-video   # Generate AI videos
POST /api/media/viral-content    # Create viral content
```

### Payment & Subscriptions
```bash
POST /api/payments/create        # Create payment
POST /api/payments/verify        # Verify payment
GET  /api/subscriptions          # Get subscription status
```

## 🎯 Common Patterns

### Backend API Pattern
```python
@app.post("/api/v1/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_verified_user)
):
    return await campaign_service.create_campaign(db, campaign_data, current_user.id)
```

### Frontend API Pattern
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['campaigns', userId],
  queryFn: () => api.getCampaigns(),
});
```

## 🌍 Localization (Indian Market)

- **Currency**: Indian Rupee (₹) throughout the platform
- **Payment Methods**: UPI, Net Banking, Cards via Razorpay
- **Language**: English with Indian business terminology
- **Time Zone**: IST (Indian Standard Time) support
- **Compliance**: Indian data protection and business regulations

## 📞 Support & Documentation

### Development Resources
- **Environment Setup**: Complete configuration guide included
- **API Documentation**: Comprehensive endpoint documentation
- **Database Schema**: Optimized PostgreSQL setup
- **Security Guide**: Authentication and data protection

### Production Support
- **Monitoring**: Health checks and performance monitoring
- **Troubleshooting**: Common issues and solutions
- **Scaling Guide**: Performance optimization strategies
- **Backup Strategy**: Database backup and recovery procedures

## 🚧 Troubleshooting

### Common Issues
1. **Database Connection**: Check PostgreSQL service and connection string
2. **API Rate Limits**: Monitor usage and implement proper rate limiting
3. **Meta App Review**: Ensure business verification and compliance
4. **Email Delivery**: Configure SendGrid for production email service
5. **Payment Integration**: Test UPI payments in sandbox mode first

### Debug Commands
```bash
# Check all service configurations
python -c "
import os
services = {
    'Google AI': os.getenv('API_KEY'),
    'Database': os.getenv('DATABASE_URL'), 
    'Razorpay': os.getenv('RAZORPAY_KEY_ID'),
    'SendGrid': os.getenv('SENDGRID_API_KEY'),
    'Meta': os.getenv('FACEBOOK_APP_ID')
}
for name, key in services.items():
    print(f'{"✅" if key else "❌"} {name}: {"Configured" if key else "Missing"}')
"
```

## 📄 License

This is a proprietary SaaS application. All rights reserved.

---

**Built with ❤️ for Indian businesses** - Empowering entrepreneurs with AI-powered marketing automation.

For technical support, check the troubleshooting section or review the comprehensive setup guides included in this documentation.