import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_ai_provider, get_jsearch_service
from app.exceptions.handlers import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Career Copilot Backend",
    version="1.0.0",
    debug=True if settings.ENV == "development" else False
)

# CORS Configuration
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Welcome to MockAI API Service!"}

@app.get("/health", summary="Health Check Endpoint")
async def health_check(
    db: AsyncSession = Depends(get_db),
    ai = Depends(get_ai_provider),
    jsearch = Depends(get_jsearch_service)
):
    # Check DB Connection
    db_status = "error"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Health Check - DB Error: {e}")
        db_status = "error"

    # Check Gemini API Key status
    gemini_status = "ok" if ai.api_key else "mock_mode"
    
    # Check JSearch API Key status
    jsearch_status = "ok" if jsearch.api_key else "mock_mode"

    overall_status = "healthy" if db_status == "ok" else "unhealthy"

    return {
        "status": overall_status,
        "services": {
            "db": db_status,
            "gemini": gemini_status,
            "jsearch": jsearch_status
        }
    }

@app.get("/api/info", summary="System Information")
async def system_info():
    return {
        "version": "1.0.0",
        "environment": settings.ENV,
        "name": settings.PROJECT_NAME
    }
