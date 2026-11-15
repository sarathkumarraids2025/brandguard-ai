import os
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR.parent, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

class Settings:
    APP_NAME: str = "BRANDGUARD AI"
    APP_VERSION: str = "2.0.0"
    TAGLINE: str = "Every Message Matters. Every Brand Deserves Consistency."
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "brandguard-ai-hackathon-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'brandguard.db')}")
    
    # Optional external AI providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    UPLOAD_PATH: str = UPLOAD_DIR
    STATIC_PATH: str = STATIC_DIR
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: set = {"pdf", "docx", "txt", "csv", "png", "jpg", "jpeg", "webp"}
    
    # SSRF Protection: Block private network ranges
    FORBIDDEN_HOSTS: List[str] = [
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "169.254.169.254", "metadata.google.internal"
    ]

settings = Settings()
