import os
import pytest
from fastapi.testclient import TestClient


# Ensure tests use an in-memory sqlite database to avoid requiring Postgres for unit tests
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
from app.main import app


client = TestClient(app)




def test_signup_and_login():
    payload = {"email": "alice@example.com", "password": "secret123"}
    r = client.post("/signup", json=payload)
    assert r.status_code == 200
    json_rb = r.json()
    assert "access_token" in json_rb


    # login
    r2 = client.post("/login", json=payload)
    assert r2.status_code == 200
    j = r2.json()
    assert "access_token" in j




def test_signup_duplicate():
    payload = {"email": "bob@example.com", "password": "otherpass"}
    r = client.post("/signup", json=payload)
    assert r.status_code == 200
    r2 = client.post("/signup", json=payload)
    assert r2.status_code == 400
