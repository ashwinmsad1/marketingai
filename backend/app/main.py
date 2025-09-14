"""
AI Marketing Automation Platform - Main Application
Professional FastAPI application with modular architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Core imports
from backend.core.config import settings
from backend.core.security import validate_api_keys
from backend.core.exceptions import MarketingAIException

# Database
from backend.database import init_db, check_db_connection

# API Routes
from backend.api.v1 import auth, campaigns, media, personalization
from backend.integrations.payment import payment_routes

# Middleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.middleware.tier_enforcement_middleware import TierEnforcementMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        await check_db_connection()
        logger.info("✅ Database initialized successfully")
        
        # Validate API keys
        logger.info("🔑 Validating API keys...")
        validate_api_keys()
        logger.info("✅ API keys validated")
        
        logger.info("🎉 Application startup complete")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (applied before tier enforcement)
app.add_middleware(RateLimitMiddleware)

# Tier enforcement middleware (resolves user subscription tier)
app.add_middleware(TierEnforcementMiddleware)

# Static files
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Include API routes
app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    campaigns.router,
    prefix=f"{settings.API_V1_PREFIX}/campaigns",
    tags=["Campaigns"]
)

app.include_router(
    media.router,
    prefix=f"{settings.API_V1_PREFIX}/media", 
    tags=["Media Generation"]
)

app.include_router(
    personalization.router,
    prefix=f"{settings.API_V1_PREFIX}/personalization",
    tags=["Personalization"]
)

app.include_router(
    payment_routes.router,
    prefix=f"{settings.API_V1_PREFIX}/payments",
    tags=["Payments & Subscriptions"]
)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs_url": "/docs" if settings.DEBUG else "Contact admin for API documentation"
    }


# Global exception handler
@app.exception_handler(MarketingAIException)
async def marketing_ai_exception_handler(request, exc):
    """Handle custom MarketingAI exceptions"""
    logger.error(f"MarketingAI Error: {exc}")
    return {"error": str(exc)}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )