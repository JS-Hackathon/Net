import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "MockAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development")
    
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
    GEMINI_API_KEY: str = Field(default="")
    JSEARCH_API_KEY: str = Field(default="")
    
    # Google OAuth2 Configuration
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    
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
