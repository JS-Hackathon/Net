import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field

class Settings(BaseSettings):
    PROJECT_NAME: str = "MockAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development")
    # Log every SQL statement (verbose; adds latency in dev). Off by default.
    SQL_ECHO: bool = Field(default=False)
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # Security
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    # Single key (backward-compatible)
    GEMINI_API_KEY: str = Field(default="")
    # Multiple keys for rotation (comma-separated). Takes priority over GEMINI_API_KEY.
    GEMINI_API_KEYS: str = Field(default="")
    # Cooldown duration (seconds) when a key gets rate-limited (429).
    GEMINI_KEY_COOLDOWN: int = Field(default=60)
    # Model for job matching (heavier, higher quality).
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")
    # Model for CV parsing — a lighter model with a separate, higher free-tier
    # daily quota, enough for structured extraction/OCR of a resume.
    GEMINI_PARSE_MODEL: str = Field(default="gemini-2.5-flash-lite")

    @computed_field
    @property
    def gemini_api_keys_list(self) -> List[str]:
        """Parse all available Gemini API keys into a list.
        
        Priority: GEMINI_API_KEYS (comma-separated) > GEMINI_API_KEY (single).
        Both are merged and deduplicated.
        """
        keys: list[str] = []
        if self.GEMINI_API_KEYS:
            keys.extend(k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip())
        if self.GEMINI_API_KEY and self.GEMINI_API_KEY not in keys:
            keys.append(self.GEMINI_API_KEY)
        return keys

    JSEARCH_API_KEY: str = Field(default="")
    # JSearch geographic filter. NOTE: JSearch has very sparse Vietnam coverage —
    # country="vn" returns ~0 results, so default to empty (global) to return real
    # jobs. Set explicitly only if you accept few/no results for that country.
    JSEARCH_COUNTRY: str = Field(default="")
    JSEARCH_DATE_POSTED: str = Field(default="all")
    
    # Google OAuth2 Configuration
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/google/callback")
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    
    # Cloudflare R2
    R2_BUCKET_NAME: str = Field(default="")
    R2_ACCOUNT_ID: str = Field(default="")
    R2_ACCESS_KEY_ID: str = Field(default="")
    R2_SECRET_ACCESS_KEY: str = Field(default="")
    
    # CORS
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000")

    @field_validator("DATABASE_URL")
    @classmethod
    def _require_async_driver(cls, v: str) -> str:
        # The app + Alembic use an async engine. A sync URL (e.g. plain
        # "postgresql://") silently hangs or fails, so fail fast with a clear hint.
        if "+asyncpg" not in v:
            raise ValueError(
                "DATABASE_URL must use the asyncpg driver — expected "
                "'postgresql+asyncpg://...' but got a URL without '+asyncpg'."
            )
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
