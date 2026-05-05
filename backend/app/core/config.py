from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str
    alembic_database_url: str
    redis_url: str

    storage_dir: str = "storage"
    public_storage_url: str = "/media"

    telegram_bot_token: str
    admin_telegram_ids: str

    nanobanano_api_key: str
    lava_api_key: str

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
