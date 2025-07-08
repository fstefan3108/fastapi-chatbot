from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    database_url: str
    access_token_expire_minutes: int = 30
    api_key: str
    api_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
