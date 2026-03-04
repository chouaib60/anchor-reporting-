from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "CHANGEME_IN_PRODUCTION"
    database_url: str = "postgresql+asyncpg://raas:raas@localhost:5432/raas"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_templates: str = "templates"
    minio_bucket_outputs: str = "outputs"

    class Config: # configuration de pydantic pour charger les valeurs depuis .env file
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache() 
def get_settings() -> Settings:
    return Settings()