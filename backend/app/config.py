"""Application configuration management"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/face_detection_db"
    )
    
    # API Configuration
    api_title: str = "Face Detection Video Streaming API"
    api_version: str = "1.0.0"
    api_description: str = "Real-time face detection and ROI tracking system"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Debug mode
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Video streaming settings
    max_frame_size: int = 1920 * 1080 * 3  # 1920x1080 RGB
    video_buffer_size: int = 30  # frames to buffer
    detection_confidence_threshold: float = 0.5
    
    # Service settings
    face_detection_model: str = "mediapipe"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
