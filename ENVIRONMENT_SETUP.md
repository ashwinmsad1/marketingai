# Environment Variables Setup Guide

## 🔧 Complete Environment Configuration

This document covers all required environment variables for the **AI Marketing Automation Platform**.

## 📋 Quick Setup Checklist

### Required for Basic Operation
- ✅ **Google AI API** - Content generation (images & videos)
- ✅ **PostgreSQL Database** - Core data storage
- ✅ **JWT Security Keys** - Authentication
- ✅ **Email Service** - User verification & notifications

### Required for Payments
- ✅ **Stripe** - International payments & subscriptions  
- ✅ **UPI Gateway** - Indian market payments (Razorpay/PayU)
- ✅ **Google Pay** - Seamless payment integration

### Required for Meta Integration
- ✅ **Facebook App** - Meta API access
- ✅ **Meta OAuth** - User account connections

### Required for Production
- ⚠️ **SendGrid** - Email delivery service (CRITICAL for production)

---

## 🎨 AI Content Generation

### Google AI (Gemini + Veo)
```bash
# Google AI API for content generation (REQUIRED)
API_KEY=your_google_ai_api_key_here

# Alternative AI provider (optional)
OPEN_ROUTER_API_KEY=your_open_router_key_here

# Google Cloud (optional - for enhanced features)
GOOGLE_CLOUD_PROJECT=your_project_id
```

**Setup Instructions:**
1. Go to https://aistudio.google.com/app/apikey
2. Create new API key
3. Enable Gemini and Veo models
4. Add to your `.env` file

---

## 💾 Database Configuration

### PostgreSQL (Primary Database)
```bash
# Complete database URL (REQUIRED)
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_marketing_platform

# Individual components (for flexibility)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_marketing_platform
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Connection Pool Settings (optional)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_SSL_MODE=prefer
```

**Setup Instructions:**
1. Install PostgreSQL 14+ 
2. Create database: `createdb ai_marketing_platform`
3. Run migrations: `alembic upgrade head`

---

## 💳 Payment Processing

### Stripe (International Payments)
```bash
# Stripe API keys (REQUIRED for payments)
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Stripe Price IDs for each tier
STRIPE_STARTER_PRICE_ID=price_starter_id_here
STRIPE_PROFESSIONAL_PRICE_ID=price_professional_id_here  
STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_id_here
```

### UPI Payment Gateway (Indian Market)
```bash
# UPI Configuration (REQUIRED for Indian users)
UPI_ENVIRONMENT=production  # sandbox or production
UPI_GATEWAY=razorpay        # razorpay, payu, or cashfree
UPI_GATEWAY_KEY=your_razorpay_key_here
UPI_GATEWAY_SECRET=your_razorpay_secret_here
UPI_WEBHOOK_SECRET=your_upi_webhook_secret

# Merchant Details
UPI_MERCHANT_ID=MERCHANT001
UPI_MERCHANT_NAME=AI Marketing Automation
UPI_MERCHANT_VPA=merchant@paytm
```

### Google Pay Integration
```bash
# Google Pay Configuration (REQUIRED for seamless payments)
GOOGLE_PAY_ENVIRONMENT=PRODUCTION    # TEST or PRODUCTION
GOOGLE_PAY_GATEWAY=stripe           # Payment processor
GOOGLE_PAY_GATEWAY_MERCHANT_ID=your_merchant_id
GOOGLE_PAY_MERCHANT_NAME=AI Marketing Automation
```

**Payment Setup Instructions:**
1. **Stripe**: Create account at https://stripe.com
2. **Razorpay**: Create account at https://razorpay.com (for UPI)
3. **Google Pay**: Configure in Stripe dashboard or payment processor

---

## 📱 Meta Marketing API

### Facebook App Configuration
```bash
# Facebook App (REQUIRED for Meta integration)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# OAuth Configuration  
FACEBOOK_REDIRECT_URI=https://yourplatform.com/auth/callback

# Default Page/Account IDs (for demo/testing)
FACEBOOK_PAGE_ID=your_default_page_id
INSTAGRAM_BUSINESS_ID=your_instagram_business_id
META_ACCESS_TOKEN=your_long_lived_token
META_AD_ACCOUNT_ID=your_ad_account_id
```

**Meta Setup Instructions:**
1. Create app at https://developers.facebook.com
2. Add Facebook Login product
3. Configure OAuth redirect URIs
4. Submit for App Review (required for production)

---

## 📧 Email Service Configuration

### SendGrid (Production Email Service)
```bash
# SendGrid Configuration (REQUIRED for production)
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here

# Email System Settings (REQUIRED)
EMAIL_SECRET_KEY=your-email-secret-key-change-in-production-256-bits-minimum
VERIFICATION_TOKEN_EXPIRE_HOURS=24
RESET_TOKEN_EXPIRE_HOURS=1

# Email Verification Settings (configured automatically)
EMAIL_VERIFICATION_REQUIRED=true
EMAIL_RESEND_COOLDOWN_SECONDS=60
```

**Email Verification Features:**
- ✅ **Automatic email verification on registration**
- ✅ **Protected features require verification**:
  - Campaign creation
  - AI content generation  
  - Subscription management
  - Payment processing
- ✅ **Resend verification with rate limiting**
- ✅ **Professional email templates**
- ✅ **Graceful fallback to console logging** (development)

**Setup Instructions:**
1. Create SendGrid account at https://sendgrid.com
2. Complete sender identity verification (required by SendGrid)
3. Create API key with "Mail Send" permissions
4. Add API key to environment variables
5. Test email verification flow

**Development vs Production:**
```bash
# Development (console logging)
# SENDGRID_API_KEY not required - emails logged to console

# Production (REQUIRED)
SENDGRID_API_KEY=SG.your_production_api_key_here
```

---

## 🔐 Security Configuration

### Authentication & JWT
```bash
# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=your-super-secret-jwt-key-256-bits-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Enhanced Security Features (implemented)
USER_EMAIL_VERIFICATION_REQUIRED=true
PROTECTED_ENDPOINTS_REQUIRE_VERIFICATION=true
RATE_LIMITING_ENABLED=true
```

---

## 🌐 External APIs

### Trend Analysis & Social APIs
```bash
# Social Media APIs (optional - for viral content detection)
TWITTER_API_KEY=your_twitter_api_key
NEWS_API_KEY=your_news_api_key

# Already configured above
GOOGLE_API_KEY=your_google_api_key  # Same as AI API
```

---

## ⚙️ Application Settings

### Environment & Debugging
```bash
# Application Environment
ENVIRONMENT=production     # development, staging, or production
DEBUG=False               # Set to False in production
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL

# File Upload Settings
MAX_UPLOAD_SIZE=50MB

# CORS Settings (for production)
ALLOWED_ORIGINS=https://yourplatform.com,https://www.yourplatform.com
```

---

## 📁 File Structure

Create these files in your project root:

```
/your-project/
├── .env                 # Main environment file (DO NOT COMMIT)
├── .env.example         # Template (safe to commit)
├── .env.local          # Local overrides (DO NOT COMMIT)
├── .env.production     # Production config (DO NOT COMMIT)
└── .env.staging        # Staging config (DO NOT COMMIT)
```

---

## 🚀 Production Deployment

### Docker Environment Variables
```dockerfile
# In your docker-compose.yml or Dockerfile
ENV API_KEY=${API_KEY}
ENV DATABASE_URL=${DATABASE_URL}
ENV STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
ENV FACEBOOK_APP_SECRET=${FACEBOOK_APP_SECRET}
# ... add all required variables
```

### Environment Validation
```bash
# Check required variables are set
python -c "
import os

# Core required variables
required = [
    'API_KEY', 'DATABASE_URL', 'JWT_SECRET_KEY', 'EMAIL_SECRET_KEY'
]

# Production-specific requirements
production = [
    'STRIPE_SECRET_KEY', 'SENDGRID_API_KEY'
]

# Check core requirements
missing = [var for var in required if not os.getenv(var)]
if missing:
    print(f'❌ Missing required variables: {missing}')
    exit(1)

print('✅ Core environment variables are set')

# Check production requirements
env = os.getenv('ENVIRONMENT', 'development')
if env == 'production':
    missing_prod = [var for var in production if not os.getenv(var)]
    if missing_prod:
        print(f'⚠️  Production deployment missing: {missing_prod}')
        print('   Note: SENDGRID_API_KEY required for email delivery')
    else:
        print('✅ Production environment variables are set')

# Check email system status
print('\n📧 Email System Status:')
email_features = {
    'Email Secret Key': '✅' if os.getenv('EMAIL_SECRET_KEY') else '❌',
    'SendGrid API Key': '✅' if os.getenv('SENDGRID_API_KEY') else '📝 Development',
    'Verification Tokens': '24 hours expiry',
    'Rate Limiting': '60 seconds cooldown',
    'Protected Features': 'Campaigns, AI Generation, Payments'
}

for feature, status in email_features.items():
    print(f'  {status} {feature}')
"
```

**Test Email Verification System:**
```bash
# 1. Start application
python api_server.py

# 2. Register new user (check console for verification email)
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{\"email\":\"test@example.com\", \"password\":\"password123\", \"first_name\":\"Test\"}'

# 3. Try accessing protected endpoint (should fail)
curl -X POST http://localhost:8000/api/campaigns \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
  # Should return 403 - Email verification required

# 4. Verify email and retry (should succeed)
```

---

## 🔒 Security Best Practices

### DO NOT COMMIT SECRETS
```bash
# Add to .gitignore (IMPORTANT)
.env
.env.local
.env.production
.env.staging
*.env
config/secrets.json
credentials.json
```

### Production Security
1. **Use strong secret keys** (256-bit minimum)
2. **Rotate keys regularly** (quarterly)
3. **Use environment-specific configs**
4. **Enable SSL/TLS everywhere**
5. **Monitor for secret leaks**
6. **Use vault services** (AWS Secrets Manager, HashiCorp Vault)

### Development vs Production
```bash
# Development
DEBUG=True
STRIPE_SECRET_KEY=sk_test_...
GOOGLE_PAY_ENVIRONMENT=TEST

# Production  
DEBUG=False
STRIPE_SECRET_KEY=sk_live_...
GOOGLE_PAY_ENVIRONMENT=PRODUCTION
```

---

## 🚨 Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check `.env` file exists and is loaded
   - Verify no typos in variable names
   - Restart application after changes

2. **Database connection failed**
   - Check PostgreSQL is running
   - Verify connection string format
   - Test with: `psql $DATABASE_URL`

3. **Email verification errors**
   - **"Email verification required"** (403 error)
     - User needs to verify email before accessing protected features
     - Check console for verification link (development)
     - Ensure user clicks verification email link
   - **"Email not sent"**
     - Development: Check console output for verification link
     - Production: Verify SENDGRID_API_KEY is set and valid
     - Check SendGrid account status and sender verification
   - **"Verification token expired"**
     - Tokens expire after 24 hours
     - Use resend functionality to get new token
     - Check VERIFICATION_TOKEN_EXPIRE_HOURS setting

4. **SendGrid integration issues**
   - **"Invalid API key"**
     - Verify API key starts with 'SG.'
     - Check API key has 'Mail Send' permissions
     - Ensure sender identity is verified in SendGrid
   - **"Emails not delivered"**
     - Check spam folder
     - Verify sender identity verification completed
     - Set up domain authentication for better deliverability

5. **Payment integration errors**
   - Verify API keys are for correct environment (test/live)
   - Check webhook endpoints are accessible
   - Validate merchant configurations

6. **Meta API permission errors**
   - Complete Facebook App Review process
   - Verify OAuth redirect URIs match exactly
   - Check token expiration and refresh

### Environment Loading Order
```python
# Python-dotenv loads in this order:
1. .env.local           # Local overrides (highest priority)
2. .env.development     # Environment-specific
3. .env                 # Default environment file
4. System environment   # OS environment variables (lowest priority)
```

---

## 📞 Support

For environment setup issues:
1. Check logs with `LOG_LEVEL=DEBUG`
2. Validate each service independently  
3. Test with minimal configuration first
4. Review service provider documentation

**Service Documentation:**
- Google AI: https://ai.google.dev/docs
- Stripe: https://docs.stripe.com
- Meta API: https://developers.facebook.com/docs
- Razorpay: https://razorpay.com/docs