import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_swagger_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

def test_redoc_docs_available():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "ReDoc" in response.text
