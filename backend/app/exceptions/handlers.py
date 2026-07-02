from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.exceptions.base import AppException

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
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
            # Standardize field location display
            field = ".".join(str(loc) for loc in err.get("loc", [])[1:])
            details.append({
                "field": field or "body",
                "message": err.get("msg", "Invalid value")
            })
            
        return JSONResponse(
            status_code=422,
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
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": 500,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": [str(exc)] if app.debug else [],
                "path": str(request.url.path),
            },
        )
