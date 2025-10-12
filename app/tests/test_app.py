import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared"

from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    yield

client = TestClient(app)

def test_signup_and_login():
    payload = {"email": "alice@example.com", "password": "secret123"}
    r = client.post("/signup", json=payload)
    assert r.status_code == 200
    assert "access_token" in r.json()

    r2 = client.post("/login", json=payload)
    assert r2.status_code == 200
    assert "access_token" in r2.json()
