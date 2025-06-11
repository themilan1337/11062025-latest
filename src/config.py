from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Task Management API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database settings
    database_url: str
    postgres_user: str = "user"
    postgres_password: str = "password"
    postgres_db: str = "taskdb"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # JWT settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # AI API Keys
    openai_api_key: str = ""
    mistral_api_key: str = ""
    
    # Web Scraping settings
    scrape_url: str = "https://example.com/data"
    scrape_interval_hours: int = 24
    
    class Config:
        env_file = ".env"

settings = Settings()
