from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic for validation and type safety.
    """

    # Application
    APP_NAME: str = "Xacari Workout Coach API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]  # Allow all origins for development
    CORS_ALLOW_CREDENTIALS: bool = False  # Must be False when origins is *
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MESSAGE_QUEUE_SIZE: int = 100

    # Supabase (to be filled in by user)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # AI Model
    POSE_MODEL_NAME: str = "movenet"  # or "rtmpose"
    POSE_CONFIDENCE_THRESHOLD: float = 0.5
    MODEL_DEVICE: str = "cpu"  # cpu or cuda

    # Workout Session
    MAX_SESSION_DURATION: int = 7200  # 2 hours in seconds
    POSE_ANALYSIS_FPS: int = 10  # Frames per second for pose analysis

    # Voice Agent
    VOICE_ENABLED: bool = True
    TTS_MODEL: str = "parler-tts/parler-tts-mini-v1"  # Hugging Face model
    HF_TOKEN: Optional[str] = None  # Hugging Face API token

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to avoid re-reading environment variables.
    """
    return Settings()


# Global settings instance
settings = get_settings()
