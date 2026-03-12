from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "WebFactory"
    secret_key: str = "change-me-in-production"
    token_expiry_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite+aiosqlite:///./webfactory.db"
    tick_rate_hz: int = 10
    autosave_interval_seconds: int = 10
    max_players_per_world: int = 16


settings = Settings()
