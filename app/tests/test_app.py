import os
import pytest
from fastapi.testclient import TestClient

# Utiliser une base SQLite en mémoire pour les tests
os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared"

from app.main import app
from app.database import init_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Initialise la base avant les tests"""
    init_db()
    yield


client = TestClient(app)


def test_api_signup_and_login():
    """Teste l'inscription et la connexion via API JSON"""
    payload = {"email": "alice@example.com", "password": "secret123"}

    # Test API signup
    r = client.post("/api/signup", json=payload)
    assert r.status_code == 200, f"Erreur signup: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test API login
    r2 = client.post("/api/login", json=payload)
    assert r2.status_code == 200, f"Erreur login: {r2.text}"
    data2 = r2.json()
    assert "access_token" in data2
    assert data2["token_type"] == "bearer"


def test_html_signup_and_login():
    """Teste les formulaires HTML"""
    payload = {"email": "bob@example.com", "password": "mypassword"}

    # Test formulaire signup
    r = client.post("/signup", data=payload, follow_redirects=False)
    assert r.status_code in (200, 303), f"Erreur signup HTML: {r.text}"

    # Test formulaire login
    r2 = client.post("/login", data=payload, follow_redirects=True)
    assert r2.status_code == 200, f"Erreur login HTML: {r2.text}"
    assert "Bienvenue" in r2.text or "token" in r2.text


def test_healthcheck():
    """Teste la route /health"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
