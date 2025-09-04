#!/usr/bin/env python3
"""
Database initialization script for personalization features
Creates and configures the enhanced database schema with all personalization tables
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, MetaUserProfile, CampaignRecommendation
from database.connection import get_database_url, create_database_engine
from database.config import get_database_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PersonalizationDatabaseInitializer:
    """Initialize and configure the enhanced personalization database schema"""
    
    def __init__(self):
        """Initialize the database initializer"""
        self.config = get_database_config()
        self.database_url = get_database_url()
        self.engine = None
        self.session_factory = None
        
    async def initialize_database(self):
        """Complete database initialization process"""
        try:
            logger.info("Starting personalization database initialization...")
            
            # 1. Create database engine
            await self._create_engine()
            
            # 2. Run database migrations
            await self._run_migrations()
            
            # 3. Verify schema creation
            await self._verify_schema()
            
            # 4. Create default templates
            await self._create_default_templates()
            
            # 5. Set up monitoring
            await self._setup_monitoring()
            
            logger.info("Personalization database initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
            
    async def _create_engine(self):
        """Create database engine and session factory"""
        try:
            self.engine = create_database_engine()
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("Database engine created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
            
    async def _run_migrations(self):
        """Run Alembic migrations to create the new schema"""
        try:
            # Configure Alembic
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
            
            # Run migrations
            logger.info("Running database migrations...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
            
    async def _verify_schema(self):
        """Verify that all new tables were created correctly"""
        try:
            logger.info("Verifying database schema...")
            
            with self.engine.connect() as connection:
                # Check that all new tables exist
                new_tables = [
                    'meta_user_profiles',
                    'campaign_recommendations', 
                    'ab_tests',
                    'test_variations',
                    'test_results',
                    'learning_insights',
                    'performance_patterns',
                    'content_templates',
                    'personalized_content',
                    'campaign_personalization_settings'
                ]
                
                for table_name in new_tables:
                    result = connection.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table_name}'
                        );
                    """))
                    
                    exists = result.scalar()
                    if not exists:
                        raise Exception(f"Table {table_name} was not created")
                    
                logger.info(f"Verified {len(new_tables)} new tables created successfully")
                
                # Check indexes
                result = connection.execute(text("""
                    SELECT COUNT(*) FROM pg_indexes 
                    WHERE tablename IN (
                        'meta_user_profiles', 'campaign_recommendations', 'ab_tests',
                        'test_variations', 'test_results', 'learning_insights',
                        'performance_patterns', 'content_templates', 'personalized_content',
                        'campaign_personalization_settings'
                    );
                """))
                
                index_count = result.scalar()
                logger.info(f"Verified {index_count} performance indexes created")
                
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            raise
            
    async def _create_default_templates(self):
        """Create default content templates for common use cases"""
        try:
            logger.info("Creating default content templates...")
            
            session = self.session_factory()
            
            default_templates = [
                {
                    "template_id": "default_image_ecommerce",
                    "name": "E-commerce Product Showcase",
                    "description": "High-converting product showcase template for e-commerce",
                    "template_type": "image",
                    "category": "ecommerce",
                    "base_prompt": "Create a professional product showcase image featuring {product_name} with {brand_colors} color scheme, showcasing {key_benefits} for {target_demographic}",
                    "personalization_variables": {
                        "product_name": "string",
                        "brand_colors": "array",
                        "key_benefits": "array", 
                        "target_demographic": "string"
                    },
                    "target_industries": ["ecommerce", "retail", "fashion"],
                    "target_objectives": ["sales", "brand_awareness"],
                    "is_public": True,
                    "created_by": "system"
                },
                {
                    "template_id": "default_video_services",
                    "name": "Service-Based Business Video",
                    "description": "Engaging video template for service-based businesses",
                    "template_type": "video",
                    "category": "services",
                    "base_prompt": "Create a professional service showcase video for {business_name} highlighting {service_benefits} with {brand_voice} tone, targeting {target_age_group}",
                    "personalization_variables": {
                        "business_name": "string",
                        "service_benefits": "array",
                        "brand_voice": "enum",
                        "target_age_group": "enum"
                    },
                    "target_industries": ["consulting", "healthcare", "finance"],
                    "target_objectives": ["lead_generation", "brand_awareness"],
                    "is_public": True,
                    "created_by": "system"
                },
                {
                    "template_id": "default_carousel_multi",
                    "name": "Multi-Product Carousel",
                    "description": "Carousel template showcasing multiple products or services",
                    "template_type": "carousel", 
                    "category": "multi_product",
                    "base_prompt": "Create a {slide_count}-slide carousel showcasing {products} with consistent {brand_colors} theme, each slide highlighting {unique_selling_points}",
                    "personalization_variables": {
                        "slide_count": "integer",
                        "products": "array",
                        "brand_colors": "array",
                        "unique_selling_points": "array"
                    },
                    "target_industries": ["ecommerce", "saas", "education"],
                    "target_objectives": ["engagement", "traffic"],
                    "is_public": True,
                    "created_by": "system"
                }
            ]
            
            from database.models import ContentTemplate
            import uuid
            
            for template_data in default_templates:
                template = ContentTemplate(
                    id=str(uuid.uuid4()),
                    template_id=template_data["template_id"],
                    name=template_data["name"],
                    description=template_data["description"],
                    template_type=template_data["template_type"],
                    category=template_data["category"],
                    base_prompt=template_data["base_prompt"],
                    personalization_variables=template_data["personalization_variables"],
                    target_industries=template_data["target_industries"],
                    target_objectives=template_data["target_objectives"],
                    is_public=template_data["is_public"],
                    created_by=template_data["created_by"],
                    is_active=True,
                    usage_count=0,
                    created_at=datetime.now()
                )
                session.add(template)
                
            session.commit()
            session.close()
            
            logger.info(f"Created {len(default_templates)} default content templates")
            
        except Exception as e:
            logger.error(f"Failed to create default templates: {e}")
            raise
            
    async def _setup_monitoring(self):
        """Set up basic monitoring for the new tables"""
        try:
            logger.info("Setting up database monitoring...")
            
            with self.engine.connect() as connection:
                # Create monitoring views for key metrics
                monitoring_views = [
                    """
                    CREATE OR REPLACE VIEW personalization_metrics AS
                    SELECT 
                        COUNT(DISTINCT mup.user_id) as users_with_profiles,
                        COUNT(DISTINCT cr.user_id) as users_with_recommendations,
                        COUNT(DISTINCT ab.user_id) as users_with_ab_tests,
                        COUNT(DISTINCT li.user_id) as users_with_insights,
                        AVG(cr.confidence_score) as avg_recommendation_confidence
                    FROM meta_user_profiles mup
                    FULL OUTER JOIN campaign_recommendations cr ON mup.user_id = cr.user_id
                    FULL OUTER JOIN ab_tests ab ON mup.user_id = ab.user_id  
                    FULL OUTER JOIN learning_insights li ON mup.user_id = li.user_id;
                    """,
                    """
                    CREATE OR REPLACE VIEW ab_test_performance AS
                    SELECT 
                        ab.status,
                        ab.test_type,
                        COUNT(*) as test_count,
                        AVG(ab.confidence_level) as avg_confidence,
                        COUNT(CASE WHEN ab.significance_status = 'significant' THEN 1 END) as significant_tests
                    FROM ab_tests ab
                    GROUP BY ab.status, ab.test_type;
                    """,
                    """
                    CREATE OR REPLACE VIEW content_template_performance AS
                    SELECT 
                        ct.template_type,
                        ct.category,
                        COUNT(*) as template_count,
                        AVG(ct.usage_count) as avg_usage,
                        AVG(ct.avg_performance_score) as avg_performance,
                        AVG(ct.success_rate) as avg_success_rate
                    FROM content_templates ct
                    WHERE ct.is_active = true
                    GROUP BY ct.template_type, ct.category;
                    """
                ]
                
                for view_sql in monitoring_views:
                    connection.execute(text(view_sql))
                    
                connection.commit()
                
            logger.info("Database monitoring views created successfully")
            
        except Exception as e:
            logger.error(f"Failed to set up monitoring: {e}")
            raise

    async def create_sample_data(self, user_id: str):
        """Create sample personalization data for testing"""
        try:
            logger.info(f"Creating sample personalization data for user {user_id}")
            
            session = self.session_factory()
            
            # Create sample MetaUserProfile
            from database.models import (
                MetaUserProfile, BusinessSizeEnum, BudgetRangeEnum, 
                CampaignObjectiveEnum, BrandVoiceEnum, ContentPreferenceEnum
            )
            
            profile = MetaUserProfile(
                id=str(uuid.uuid4()),
                user_id=user_id,
                business_size=BusinessSizeEnum.SMB,
                industry="ecommerce",
                business_name="Sample E-commerce Store",
                monthly_budget=BudgetRangeEnum.MEDIUM,
                primary_objective=CampaignObjectiveEnum.SALES,
                secondary_objectives=["brand_awareness", "traffic"],
                target_age_groups=["millennial", "gen_x"],
                target_locations=["united_states", "canada"],
                target_interests=["shopping", "fashion", "lifestyle"],
                brand_voice=BrandVoiceEnum.PROFESSIONAL,
                content_preference=ContentPreferenceEnum.IMAGE_HEAVY,
                platform_priorities=["instagram", "facebook"],
                brand_colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
                roi_focus=True,
                risk_tolerance="medium",
                automation_level="high",
                created_at=datetime.now()
            )
            
            session.add(profile)
            session.commit()
            session.close()
            
            logger.info("Sample personalization data created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            raise

async def main():
    """Main initialization function"""
    initializer = PersonalizationDatabaseInitializer()
    
    try:
        # Initialize the database
        await initializer.initialize_database()
        
        # Optionally create sample data (uncomment to use)
        # await initializer.create_sample_data("sample-user-id")
        
        print("✅ Personalization database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Run your application to test the new personalization features")
        print("2. Use the API endpoints to create user profiles and recommendations")
        print("3. Monitor performance using the created monitoring views")
        print("4. Review the PERSONALIZATION_DATABASE_ARCHITECTURE.md for detailed documentation")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Add missing import
    import uuid
    asyncio.run(main())