import pytest
from app.core.config import settings

def test_settings_env():
    assert settings.PROJECT_NAME
    assert settings.DATABASE_URL
    assert settings.JWT_SECRET_KEY
    assert settings.API_V1_STR == "/api/v1"
