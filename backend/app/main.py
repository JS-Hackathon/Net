import logging
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, engine
from app.core.dependencies import get_ai_provider, get_jsearch_service
from app.exceptions.handlers import register_exception_handlers
from app.models import Base

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

@app.on_event("startup")
async def startup_event():
    if settings.DATABASE_URL.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created SQLite database tables successfully.")


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

# Mount Static Files (for uploads and exports fallbacks)
from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "exports"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.upload import router as upload_router
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
from app.api.v1.resumes import router as resumes_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.matching import router as matching_router
from app.api.v1.jobs import router as jobs_router

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(analyses_router, prefix=settings.API_V1_STR)
app.include_router(profiles_router, prefix=settings.API_V1_STR)
app.include_router(matching_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)



# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")
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
