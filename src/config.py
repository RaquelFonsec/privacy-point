import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Debug
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Serviços de OCR
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
    PADDLE_OCR_ENABLED = os.getenv("PADDLE_OCR_ENABLED", "False").lower() == "true"
    
    # AWS Services
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_TEXTRACT_ENABLED = os.getenv("AWS_TEXTRACT_ENABLED", "False").lower() == "true"
    
    # Azure Services
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    AZURE_ENABLED = os.getenv("AZURE_ENABLED", "False").lower() == "true"
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_DOCUMENT_AI_ENABLED = os.getenv("GOOGLE_DOCUMENT_AI_ENABLED", "False").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./privacy_point.db")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/privacy_point")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "1"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # File Storage
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Quality Control
    MIN_QUALITY_SCORE = float(os.getenv("MIN_QUALITY_SCORE", "0.8"))
    MAX_REVISION_ATTEMPTS = int(os.getenv("MAX_REVISION_ATTEMPTS", "3"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se todas as configurações obrigatórias estão presentes"""
        required_vars = [
            "OPENAI_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
            return False
        
        return True

config = Config()
