from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Discord
    discord_token: str = ""

    # S3-compatible storage
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "ttrpg-dataset-raw"
    s3_endpoint: str = ""

    # Local buffer
    local_buffer_dir: Path = Path("./sessions")

    # Logging
    log_level: str = "INFO"

    # Consent
    require_all_consent: bool = True
    consent_timeout_seconds: int = 300  # 5 minutes
    consent_grace_seconds: int = 120  # 2 more minutes after reminder

    # Recording
    min_session_duration_seconds: int = 60  # quality flag threshold
    min_participants: int = 2  # quality flag threshold


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
