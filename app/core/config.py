from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Lu Styles Sales"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SENTRY_SECRET_KEY: str
    SENTRY_ENVIRONMENT: str = ""
    SENTRY_DSN: str = ""
    SENTRY_REDIS_HOST: str
    SENTRY_TSDB: str = "sentry.tsdb.redisnuba.RedisSnubaTSDB"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    WA_API_URL: str
    WA_API_KEY: str
    WA_INSTANCE_NAME: str
    WA_AUTHENTICATION_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
