"""FrameProof Application Configuration.

Purpose: Centralized settings management via Pydantic Settings.
Inputs: Environment variables or .env file.
Outputs: Immutable application settings instance.
Status: Implemented
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration settings for FrameProof."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "FrameProof Forensic Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Air-gapped / offline enforcement
    AIR_GAPPED_MODE: bool = True
    ALLOW_OUTBOUND_NETWORK: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./frameproof_test.db"

    # Redis Queue
    REDIS_URL: str = "redis://localhost:6379/0"

    # Forensic Evidence Mounts
    EVIDENCE_VAULT_PATH: Path = Path("./data/evidence")
    CASE_STORAGE_PATH: Path = Path("./data/cases")
    TEMP_CARVE_PATH: Path = Path("./data/scratch")
    CUSTODY_LOG_PATH: Path = Path("./data/custody/custody_chain.jsonl")


settings = Settings()
