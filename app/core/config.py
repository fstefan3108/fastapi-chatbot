from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    database_url_async: str
    database_url_sync: str
    access_token_expire_minutes: int = 30
    openrouter_api_key: str
    api_url: str
    redis_url: str
    base_url: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
