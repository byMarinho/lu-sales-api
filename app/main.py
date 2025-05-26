import sentry_sdk
from fastapi import FastAPI

from app.api.v1.api_router import api_router
from app.core.config import settings
from app.core.logging import setup_log

sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.SENTRY_ENVIRONMENT)
setup_log()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "version": settings.VERSION}


app.include_router(api_router, prefix=settings.API_V1_STR)
