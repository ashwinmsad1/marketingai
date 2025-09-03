"""
Database CRUD operations for Competitor Analysis functionality
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from .models import (
    CompetitorContent, CompetitiveInsights, ImprovedContent, User
)

# Competitor Content Operations
class CompetitorContentCRUD:
    @staticmethod
    def create_competitor_content(
        db: Session, 
        content_id: str,
        competitor_name: str,
        platform: str,
        content_type: str,
        content_url: str,
        caption: str,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        performance_score: float = 0.0,
        analyzed_elements: Dict[str, Any] = None,
        user_id: str = None,
        discovered_at: datetime = None
    ) -> CompetitorContent:
        """Create new competitor content record"""
        
        content = CompetitorContent(
            id=str(uuid.uuid4()),
            content_id=content_id,
            user_id=user_id,
            competitor_name=competitor_name,
            platform=platform,
            content_type=content_type,
            content_url=content_url,
            caption=caption,
            likes=likes,
            comments=comments,
            shares=shares,
            performance_score=performance_score,
            analyzed_elements=analyzed_elements or {},
            discovered_at=discovered_at or datetime.utcnow()
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    
    @staticmethod
    def get_competitor_content(db: Session, content_id: str) -> Optional[CompetitorContent]:
        """Get competitor content by content_id"""
        return db.query(CompetitorContent).filter(
            CompetitorContent.content_id == content_id
        ).first()
    
    @staticmethod
    def get_competitor_content_by_id(db: Session, id: str) -> Optional[CompetitorContent]:
        """Get competitor content by database ID"""
        return db.query(CompetitorContent).filter(
            CompetitorContent.id == id
        ).first()
    
    @staticmethod
    def get_competitor_content_by_competitor(
        db: Session, 
        competitor_name: str,
        limit: int = None
    ) -> List[CompetitorContent]:
        """Get all content for a specific competitor"""
        query = db.query(CompetitorContent).filter(
            CompetitorContent.competitor_name == competitor_name
        ).order_by(desc(CompetitorContent.performance_score))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update_competitor_content(
        db: Session, 
        content_id: str, 
        **kwargs
    ) -> Optional[CompetitorContent]:
        """Update competitor content"""
        content = db.query(CompetitorContent).filter(
            CompetitorContent.content_id == content_id
        ).first()
        
        if content:
            for key, value in kwargs.items():
                setattr(content, key, value)
            content.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(content)
        
        return content
    
    @staticmethod
    def delete_competitor_content(db: Session, content_id: str) -> bool:
        """Delete competitor content"""
        content = db.query(CompetitorContent).filter(
            CompetitorContent.content_id == content_id
        ).first()
        
        if content:
            db.delete(content)
            db.commit()
            return True
        return False

# Competitive Insights Operations
class CompetitiveInsightsCRUD:
    @staticmethod
    def create_competitive_insights(
        db: Session,
        competitor_name: str,
        content_themes: List[str] = None,
        top_content_ids: List[str] = None,
        engagement_patterns: Dict[str, Any] = None,
        recommended_actions: List[str] = None,
        content_gaps: List[str] = None,
        user_id: str = None
    ) -> CompetitiveInsights:
        """Create new competitive insights record"""
        
        insights = CompetitiveInsights(
            id=str(uuid.uuid4()),
            user_id=user_id,
            competitor_name=competitor_name,
            content_themes=content_themes or [],
            top_content_ids=top_content_ids or [],
            engagement_patterns=engagement_patterns or {},
            recommended_actions=recommended_actions or [],
            content_gaps=content_gaps or []
        )
        db.add(insights)
        db.commit()
        db.refresh(insights)
        return insights
    
    @staticmethod
    def get_latest_competitive_insights(
        db: Session, 
        competitor_name: str
    ) -> Optional[CompetitiveInsights]:
        """Get latest competitive insights for a competitor"""
        return db.query(CompetitiveInsights).filter(
            CompetitiveInsights.competitor_name == competitor_name
        ).order_by(desc(CompetitiveInsights.analysis_date)).first()
    
    @staticmethod
    def get_competitive_insights_by_competitor(
        db: Session, 
        competitor_name: str
    ) -> List[CompetitiveInsights]:
        """Get all insights for a competitor"""
        return db.query(CompetitiveInsights).filter(
            CompetitiveInsights.competitor_name == competitor_name
        ).order_by(desc(CompetitiveInsights.analysis_date)).all()

# Improved Content Operations
class ImprovedContentCRUD:
    @staticmethod
    def create_improved_content(
        db: Session,
        improvement_id: str,
        user_id: str,
        original_content_id: str,
        improvement_type: str,
        new_prompt: str,
        new_caption: str,
        estimated_lift: float = 0.0,
        competitive_advantages: List[str] = None,
        generated_asset: str = None
    ) -> ImprovedContent:
        """Create improved content record"""
        
        improved = ImprovedContent(
            id=str(uuid.uuid4()),
            improvement_id=improvement_id,
            user_id=user_id,
            original_content_id=original_content_id,
            improvement_type=improvement_type,
            new_prompt=new_prompt,
            new_caption=new_caption,
            estimated_lift=estimated_lift,
            competitive_advantages=competitive_advantages or [],
            generated_asset=generated_asset
        )
        db.add(improved)
        db.commit()
        db.refresh(improved)
        return improved
    
    @staticmethod
    def get_improved_content(db: Session, improvement_id: str) -> Optional[ImprovedContent]:
        """Get improved content by improvement_id"""
        return db.query(ImprovedContent).filter(
            ImprovedContent.improvement_id == improvement_id
        ).first()
    
    @staticmethod
    def get_improved_content_by_user(
        db: Session, 
        user_id: str,
        limit: int = None
    ) -> List[ImprovedContent]:
        """Get improved content by user"""
        query = db.query(ImprovedContent).filter(
            ImprovedContent.user_id == user_id
        ).order_by(desc(ImprovedContent.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_improved_content_by_original(
        db: Session, 
        original_content_id: str
    ) -> List[ImprovedContent]:
        """Get all improvements for original content"""
        return db.query(ImprovedContent).filter(
            ImprovedContent.original_content_id == original_content_id
        ).order_by(desc(ImprovedContent.created_at)).all()
    
    @staticmethod
    def update_improved_content(
        db: Session, 
        improvement_id: str, 
        **kwargs
    ) -> Optional[ImprovedContent]:
        """Update improved content"""
        improved = db.query(ImprovedContent).filter(
            ImprovedContent.improvement_id == improvement_id
        ).first()
        
        if improved:
            for key, value in kwargs.items():
                setattr(improved, key, value)
            improved.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(improved)
        
        return improved
    
    @staticmethod
    def update_generated_asset(
        db: Session, 
        improvement_id: str, 
        generated_asset: str
    ) -> Optional[ImprovedContent]:
        """Update generated asset path"""
        return ImprovedContentCRUD.update_improved_content(
            db, improvement_id, generated_asset=generated_asset
        )

# Utility functions for complex queries
class CompetitorAnalysisUtils:
    @staticmethod
    def get_competitor_performance_stats(
        db: Session, 
        competitor_name: str
    ) -> Dict[str, Any]:
        """Get performance statistics for a competitor"""
        content_list = db.query(CompetitorContent).filter(
            CompetitorContent.competitor_name == competitor_name
        ).all()
        
        if not content_list:
            return {}
        
        scores = [c.performance_score for c in content_list if c.performance_score]
        
        return {
            'total_content': len(content_list),
            'avg_performance': sum(scores) / len(scores) if scores else 0,
            'max_performance': max(scores) if scores else 0,
            'min_performance': min(scores) if scores else 0,
            'total_engagement': sum(c.likes + c.comments + c.shares for c in content_list)
        }
    
    @staticmethod
    def get_top_performing_competitors(
        db: Session, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing competitors by average performance score"""
        # This would require more complex SQL aggregation
        # For now, return basic competitor list
        competitors = db.query(CompetitorContent.competitor_name).distinct().all()
        
        results = []
        for (competitor_name,) in competitors[:limit]:
            stats = CompetitorAnalysisUtils.get_competitor_performance_stats(
                db, competitor_name
            )
            if stats:
                results.append({
                    'competitor_name': competitor_name,
                    'performance_stats': stats
                })
        
        # Sort by average performance
        results.sort(key=lambda x: x['performance_stats']['avg_performance'], reverse=True)
        return results[:limit]