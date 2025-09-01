# Meta Marketing API Setup Guide for AI Ad Automation Platform

## 🎯 Platform Overview
You're building an **AI-powered marketing automation SaaS platform** where:
- Users pay you $29.99-$299.99/month for automation services
- Users pay Meta directly for their ad spend (no financial risk for you)
- Your platform creates and optimizes campaigns in users' Meta ad accounts

## 📋 Critical Prerequisites for YOUR Platform

### **Business Requirements**
1. **Meta Developer Account**: Create at https://developers.facebook.com
2. **Meta Business Manager**: Required for agency-style app (https://business.facebook.com)
3. **Your Business Facebook Page**: For your platform/company
4. **Domain & SSL Certificate**: For OAuth redirect URLs
5. **Business Registration**: LLC/Corporation recommended for Meta Business verification

### **Technical Requirements**
1. **Production Domain**: Cannot use localhost for Meta App Review
2. **Privacy Policy & Terms of Service**: Required for app approval
3. **Media Hosting**: AWS S3 or Google Cloud Storage (Instagram requirement)
4. **Database**: For storing user subscriptions and Meta tokens (encrypted)
5. **Payment Processing**: Stripe account for subscription billing

## Step-by-Step Setup

### 1. Create Facebook App

1. Go to https://developers.facebook.com/apps
2. Click "Create App" → "Business" → "Next"
3. Fill in app details and create app
4. Note your **App ID** and **App Secret**

### 2. Configure App Permissions

Add these permissions to your app:
- `pages_manage_posts` - Post to Facebook Pages
- `pages_read_engagement` - Read page insights
- `instagram_basic` - Access Instagram account
- `instagram_content_publish` - Post to Instagram

### 3. Generate Access Tokens

#### Page Access Token (Facebook)
1. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer
2. Select your app and request these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
3. Generate token and exchange for long-lived token

#### Instagram Business Account ID
1. Use Graph API to get your Instagram Business Account ID:
   ```bash
   GET /{page-id}?fields=instagram_business_account&access_token={access-token}
   ```

### 4. Environment Variables Setup

Add these to your `.env` file:

```bash
# Facebook/Instagram API Configuration
FACEBOOK_ACCESS_TOKEN=your_long_lived_page_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_BUSINESS_ID=your_instagram_business_account_id
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

## API Limitations & Requirements

### Facebook Video Upload
- **Max file size**: 4GB
- **Max duration**: 240 minutes
- **Supported formats**: MP4, MOV
- **Recommended**: H.264 codec, AAC audio
- **Resolution**: Up to 1080p

### Instagram Video Upload (Reels)
- **Max duration**: 90 seconds (business accounts)
- **Container**: MOV or MP4 (MPEG-4 Part 14)
- **Video codec**: HEVC or H264, progressive scan
- **Audio codec**: AAC, 48khz max, mono or stereo
- **Frame rate**: 23-60 FPS
- **Important**: Requires publicly accessible video URLs

### Rate Limits
- **Instagram**: 25 API-published posts per 24 hours
- **Facebook**: Standard Graph API rate limits apply
- **Recommendation**: Implement retry logic and rate limiting

## Production Considerations

### 1. Media Hosting
Instagram Graph API requires publicly accessible URLs for media files. Options:
- **AWS S3** with public bucket
- **Google Cloud Storage** with public access
- **Azure Blob Storage** with public container
- **CDN** for better performance

### 2. Webhook Setup
For real-time updates and analytics:
```python
# Webhook endpoint for receiving updates
@app.post("/webhook/facebook")
async def facebook_webhook(request):
    # Handle Instagram/Facebook webhook events
    pass
```

### 3. Error Handling
Common error scenarios:
- Token expiration (refresh tokens)
- Rate limiting (implement backoff)
- Media format issues (validate before upload)
- Network timeouts (retry mechanisms)

## Testing

### 1. Test with Sample Content
```bash
# Test Facebook upload
python facebook_agent.py
# Select option 1, provide video path and caption
```

### 2. Validate Permissions
Use Graph API Explorer to test API calls with your tokens.

### 3. Monitor API Usage
Check your app's API usage in Facebook Developer Console.

## App Review Process

For production apps, you may need Facebook App Review for:
- `pages_manage_posts` permission
- `instagram_content_publish` permission

Submit for review with:
- Detailed use case description
- Screen recordings of app functionality
- Privacy policy and terms of service

## Troubleshooting

### Common Issues

1. **"Invalid access token"**
   - Check token expiration
   - Verify permissions granted
   - Regenerate if necessary

2. **"Unsupported video format"**
   - Ensure MP4 with H.264 codec
   - Check file size limits
   - Validate video specifications

3. **"Media URL not accessible"**
   - For Instagram, ensure media is publicly accessible
   - Use HTTPS URLs only
   - Test URL accessibility independently

4. **Rate limit exceeded**
   - Implement exponential backoff
   - Monitor API usage quotas
   - Consider request batching

### Debug Tips

1. Enable detailed error logging
2. Test with Graph API Explorer first
3. Validate media files before upload
4. Monitor network connectivity
5. Check Facebook Developer Console for app issues

## Security Best Practices

1. **Never commit tokens to version control**
2. **Use environment variables for all credentials**
3. **Implement token refresh logic**
4. **Rotate access tokens regularly**
5. **Monitor API usage for suspicious activity**
6. **Use HTTPS for all webhook endpoints**

## Next Steps

1. Complete App Review if needed for production
2. Implement media hosting solution (S3/GCS)
3. Add webhook endpoints for real-time updates
4. Create campaign scheduling system
5. Implement analytics dashboard