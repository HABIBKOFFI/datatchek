from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DATATCHEK MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database (internal)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/datatchek"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/datatchek"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_MIN_32_CHARS"
    ENCRYPTION_KEY: str = "CHANGE_ME_FERNET_KEY_44_CHARS_BASE64"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Connection defaults
    DB_CONNECTION_TIMEOUT_SECONDS: int = 5

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
