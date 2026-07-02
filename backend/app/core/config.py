import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "MockAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development")
    
    # Database
    POSTGRES_USER: str = Field(default="root")
    POSTGRES_PASSWORD: str = Field(default="123456")
    POSTGRES_DB: str = Field(default="my_database")
    DATABASE_URL: str = Field(default="postgresql+asyncpg://root:123456@localhost:5433/my_database")

    # Security
    JWT_SECRET: str = Field(default="4036717551323267566B5970337336763979244226452F484F4D514D58753978")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    GEMINI_API_KEY: str = Field(default="")
    JSEARCH_API_KEY: str = Field(default="")
    
    # Cloudflare R2
    R2_BUCKET_NAME: str = Field(default="")
    R2_ACCOUNT_ID: str = Field(default="")
    R2_ACCESS_KEY_ID: str = Field(default="")
    R2_SECRET_ACCESS_KEY: str = Field(default="")
    
    # CORS
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
