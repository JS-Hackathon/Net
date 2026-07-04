from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.exceptions.base import AppException
from app.core.config import settings


from starlette.exceptions import HTTPException as StarletteHTTPException


def _cors_headers(request: Request) -> dict:
    """
    Build the minimum CORS headers required so that browser error responses
    are not treated as CORS failures.  FastAPI's CORSMiddleware only wraps
    the normal response path; exception-handler responses bypass it entirely.
    """
    allowed = [o.strip().rstrip("/") for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    origin = request.headers.get("origin", "")
    if origin in allowed or "*" in allowed:
        return {
            "Access-Control-Allow-Origin": origin or "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            headers={**_cors_headers(request), **(exc.headers or {})},
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": exc.status_code,
                "error": "HTTP_EXCEPTION",
                "message": exc.detail,
                "details": [],
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            headers=_cors_headers(request),
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": exc.status_code,
                "error": exc.error_code,
                "message": exc.message,
                "details": [],
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err.get("loc", [])[1:])
            details.append({
                "field": field or "body",
                "message": err.get("msg", "Invalid value")
            })

        return JSONResponse(
            status_code=422,
            headers=_cors_headers(request),
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": 422,
                "error": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": details,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            headers=_cors_headers(request),
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": 500,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": [str(exc)] if app.debug else [],
                "path": str(request.url.path),
            },
        )

