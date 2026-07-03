import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, engine
from app.core.dependencies import get_ai_provider, get_jsearch_service
from app.exceptions.handlers import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown checks: surface config + DB connectivity loudly so a
    misconfigured environment fails at boot instead of as an opaque 500 later."""
    origins = [o for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    logger.info("=" * 64)
    logger.info(f"MockAI backend starting — ENV={settings.ENV}")
    logger.info(f"CORS allowed origins: {origins}")
    logger.info(
        "Integrations configured — gemini=%s jsearch=%s google=%s r2=%s",
        bool(settings.GEMINI_API_KEY), bool(settings.JSEARCH_API_KEY),
        bool(settings.GOOGLE_CLIENT_ID), bool(settings.R2_BUCKET_NAME),
    )
    if settings.ENV != "production":
        logger.warning("ENV is not 'production' — debug mode leaks tracebacks and "
                       "drops CORS headers on 500s. Set ENV=production when deployed.")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection: OK")
    except Exception as e:  # noqa: BLE001 - report loudly, let /health be source of truth
        logger.error("!" * 64)
        logger.error(f"DATABASE CONNECTION FAILED at startup: {e}")
        logger.error("Hints: is Postgres up ('docker compose up -d')? Does DATABASE_URL "
                     "point at the right host/port? On Windows use 127.0.0.1 (not "
                     "localhost) and port 5433.")
        logger.error("!" * 64)
    logger.info("=" * 64)
    yield
    await engine.dispose()
    logger.info("MockAI backend stopped — DB engine disposed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Career Copilot Backend",
    version="1.0.0",
    debug=True if settings.ENV == "development" else False,
    lifespan=lifespan,
)

# CORS Configuration
origins = [o.strip().rstrip("/") for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing: expose per-request server time and log slow requests so we can
# tell whether latency is server-side (DB/compute) or network/connection.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}"
    if elapsed_ms > 1000:
        logger.warning(f"SLOW REQUEST {request.method} {request.url.path} took {elapsed_ms:.0f}ms")
    return response

# Register Exception Handlers
register_exception_handlers(app)

# Mount Static Files (for uploads and exports fallbacks)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "exports"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
logger.info(f"Mounted static files from: {static_dir}")

# Include API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.upload import router as upload_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(analyses_router, prefix=settings.API_V1_STR)
app.include_router(profiles_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(matches_router, prefix=settings.API_V1_STR)


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
