import os
from functools import lru_cache
from types import SimpleNamespace

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    supabase_url: str
    supabase_publishable_key: str
    supabase_secret_key: str
    database_url: str
    smtp_user: str
    smtp_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    model_config = ConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_settings():
    try:
        return Settings()
    except Exception as e:  # pragma: no cover - environment-dependent fallback
        # If settings can't be validated (e.g., missing env vars during import in
        # certain deployment environments), build a lightweight fallback object
        # sourced from environment variables to avoid import-time crashes.
        print(
            f"Warning: could not create Settings() due to: {e}; using fallback from os.environ"
        )

        def _int_env(key: str, default: int) -> int:
            val = os.environ.get(key)
            if val is None:
                return default
            try:
                return int(val)
            except Exception:
                return default

        fallback = {
            "supabase_url": os.environ.get("SUPABASE_URL", ""),
            "supabase_publishable_key": os.environ.get("SUPABASE_PUBLISHABLE_KEY", ""),
            "supabase_secret_key": os.environ.get("SUPABASE_SECRET_KEY", ""),
            "database_url": os.environ.get(
                "DATABASE_URL",
                os.environ.get(
                    "TEST_DATABASE_URL", "sqlite+aiosqlite:///./test_db.sqlite"
                ),
            ),
            "smtp_user": os.environ.get("SMTP_USER", ""),
            "smtp_password": os.environ.get("SMTP_PASSWORD", ""),
            "smtp_host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": _int_env("SMTP_PORT", 587),
        }

        return SimpleNamespace(**fallback)  # type: ignore[return-value]


settings = get_settings()
