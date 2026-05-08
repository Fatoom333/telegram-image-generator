from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str
    alembic_database_url: str
    redis_url: str

    test_database_url: str | None = None
    test_alembic_database_url: str | None = None

    storage_dir: str = "storage"

    mini_app_url: str
    telegram_bot_token: str
    admin_telegram_ids: str

    webhook_base_url: str
    telegram_webhook_path: str = "/api/telegram/webhook"
    telegram_webhook_secret: str

    nanobanano_project_id: str
    nanobanano_location: str = "global"
    nanobanano_api_key: str | None = None

    lava_api_key: str

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
