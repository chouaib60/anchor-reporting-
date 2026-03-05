from pydantic_settings import BaseSettings
from functools import lru_cache

class WorkerSettings(BaseSettings):
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://raas:raas@localhost:5432/raas"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_templates: str = "templates"
    minio_bucket_outputs: str = "outputs"
    worker_max_concurrent_jobs: int = 4
    worker_poll_interval_seconds: int = 5
    worker_job_timeout_seconds: int = 120
    worker_restart_after_jobs: int = 50
    libreoffice_path: str = "/usr/bin/libreoffice"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> WorkerSettings:
    return WorkerSettings()