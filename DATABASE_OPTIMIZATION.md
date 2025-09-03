# Database Performance Optimization

This document describes the database indexes and constraints added to optimize PostgreSQL performance for the AI Marketing Platform.

## Overview

Based on the architecture review, several critical performance issues were identified and addressed:

1. **Missing Indexes** - Added indexes for frequently queried columns
2. **Missing Constraints** - Added data validation and uniqueness constraints
3. **Query Optimization** - Composite indexes for multi-column queries
4. **Data Integrity** - Check constraints for business logic validation

## Added Indexes

### Users Table
- `idx_users_created_at` - For filtering by registration date
- `idx_users_is_active` - For active user queries
- `idx_users_is_verified` - For verified user queries
- `idx_users_company_name` - For company-based searches
- `idx_users_last_login` - For activity analysis

### Campaigns Table
- `idx_campaigns_user_id` - For user-specific campaign queries
- `idx_campaigns_status` - For status-based filtering
- `idx_campaigns_created_at` - For date-based queries
- `idx_campaigns_user_status` - Composite index for user + status queries
- `idx_campaigns_user_created` - Composite index for user + date queries

### Analytics Table
- `idx_analytics_campaign_date` - **Critical** - For campaign performance queries
- `idx_analytics_user_date` - **Critical** - For user analytics by date
- `idx_analytics_date` - For global date-based analytics
- `idx_analytics_campaign_id` - For campaign-specific analytics
- `idx_analytics_user_id` - For user-specific analytics

### Payments Table
- `idx_payments_user_id` - For user payment history
- `idx_payments_status` - For payment status filtering
- `idx_payments_user_status` - Composite index for user + status
- `idx_payments_created_at` - For payment timeline queries
- `idx_payments_provider` - For provider-based queries
- `idx_payments_provider_payment_id` - For external payment ID lookups

### Billing Subscriptions Table
- `idx_billing_subscriptions_user_id` - For user subscription queries
- `idx_billing_subscriptions_status` - For status filtering
- `idx_billing_subscriptions_tier` - For tier-based queries
- `idx_billing_subscriptions_user_status` - User + status composite
- `idx_billing_subscriptions_next_billing_date` - For billing jobs
- `idx_billing_subscriptions_expires_at` - For expiration monitoring

### Competitor Content Table
- `idx_competitor_content_competitor_name` - For competitor analysis
- `idx_competitor_content_platform` - For platform-specific queries
- `idx_competitor_content_content_type` - For content type filtering
- `idx_competitor_content_user_id` - For user-specific content
- `idx_competitor_content_discovered_at` - For timeline analysis
- `idx_competitor_content_performance_score` - For performance ranking

## Added Constraints

### Unique Constraints
- `uq_analytics_campaign_date` - Prevents duplicate analytics entries
- `uq_competitor_content_name_url` - Prevents duplicate competitor content

### Check Constraints

#### Campaign Validation
- Budget values must be non-negative
- Performance metrics (impressions, clicks, spend, conversions) must be non-negative

#### Analytics Validation
- All metrics must be non-negative
- Revenue cannot be negative

#### Payment Validation
- Payment amount must be positive

#### Subscription Validation
- Monthly price must be positive
- Usage limits must be non-negative

#### Competitor Content Validation
- Engagement metrics (likes, comments, shares) must be non-negative
- Performance score must be non-negative

## Performance Impact

### Expected Improvements

1. **Campaign Queries**: 10-50x faster for user-specific campaign filtering
2. **Analytics Queries**: 20-100x faster for date-range analytics
3. **Payment Queries**: 5-20x faster for payment history and status filtering
4. **Competitor Analysis**: 10-30x faster for content discovery and ranking

### Query Patterns Optimized

```sql
-- User campaign queries (now uses idx_campaigns_user_status)
SELECT * FROM campaigns WHERE user_id = ? AND status = 'active';

-- Analytics by date range (now uses idx_analytics_campaign_date)
SELECT * FROM analytics WHERE campaign_id = ? AND date BETWEEN ? AND ?;

-- Payment history (now uses idx_payments_user_status)
SELECT * FROM payments WHERE user_id = ? AND status = 'succeeded';

-- Competitor content ranking (now uses idx_competitor_content_performance_score)
SELECT * FROM competitor_content ORDER BY performance_score DESC LIMIT 10;
```

## Migration Instructions

### Applying the Migration

1. **Backup Database** (recommended)
   ```bash
   pg_dump ai_marketing_platform > backup_before_optimization.sql
   ```

2. **Run Migration**
   ```bash
   alembic upgrade head
   ```

3. **Verify Indexes**
   ```sql
   -- Check if indexes were created
   SELECT indexname, tablename FROM pg_indexes 
   WHERE tablename IN ('campaigns', 'analytics', 'payments', 'billing_subscriptions', 'competitor_content')
   ORDER BY tablename, indexname;
   ```

### Rolling Back (if needed)

```bash
alembic downgrade -1
```

### Index Creation Time

For large existing datasets:
- **Small datasets** (< 100k rows): < 1 minute
- **Medium datasets** (100k - 1M rows): 1-5 minutes
- **Large datasets** (> 1M rows): 5-30 minutes

**Note**: Index creation happens online and won't block reads, but may slow down writes temporarily.

## Monitoring

### Index Usage Monitoring

```sql
-- Monitor index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Query Performance Monitoring

```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
WHERE query LIKE '%campaigns%' OR query LIKE '%analytics%'
ORDER BY mean_time DESC
LIMIT 10;
```

## Best Practices

### For Developers

1. **Use Composite Indexes**: When filtering by multiple columns, ensure they match the composite index order
2. **Avoid SELECT \***: Specify only needed columns to reduce I/O
3. **Use LIMIT**: For paginated results, always use LIMIT with OFFSET
4. **Date Range Queries**: Always include date bounds for analytics queries

### For Database Operations

1. **Monitor Index Size**: Large indexes can impact write performance
2. **Regular VACUUM ANALYZE**: Keep statistics updated for optimal query planning
3. **Connection Pooling**: Use connection pooling to prevent connection overhead
4. **Regular Monitoring**: Monitor query performance and index usage

## Troubleshooting

### Common Issues

1. **Migration Fails on Existing Data**
   - Check for constraint violations before migration
   - Clean up invalid data first

2. **Query Still Slow After Migration**
   - Run ANALYZE on affected tables
   - Check if query uses the expected index with EXPLAIN

3. **Write Performance Degraded**
   - Monitor index maintenance overhead
   - Consider dropping unused indexes

### Support Commands

```sql
-- Analyze table statistics
ANALYZE campaigns;
ANALYZE analytics;
ANALYZE payments;

-- Check constraint violations
SELECT * FROM campaigns WHERE budget_daily < 0;
SELECT * FROM analytics WHERE impressions < 0;

-- Force index usage (for testing)
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM campaigns WHERE user_id = 'test' AND status = 'active';
SET enable_seqscan = on;
```

## Conclusion

These optimizations significantly improve query performance for the most common access patterns in the AI Marketing Platform. The combination of strategic indexing and data validation constraints ensures both performance and data integrity.

Regular monitoring and maintenance of these indexes will ensure continued optimal performance as the dataset grows.