import os
import pytest
from fastapi.testclient import TestClient

# Utilise une base SQLite en mémoire pour les tests
os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared"

from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Initialisation de la base de données avant les tests"""
    init_db()
    yield


client = TestClient(app)


def test_api_signup_and_login():
    """Teste le cycle complet d'inscription et de connexion via l'API JSON"""
    payload = {"email": "alice@example.com", "password": "secret123"}

    # --- Test /api/signup ---
    r = client.post("/api/signup", json=payload)
    assert r.status_code == 200, f"Erreur signup: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # --- Test /api/login ---
    r2 = client.post("/api/login", json=payload)
    assert r2.status_code == 200, f"Erreur login: {r2.text}"
    data2 = r2.json()
    assert "access_token" in data2
    assert data2["token_type"] == "bearer"


def test_html_signup_and_login():
    """Teste les formulaires HTML (interface utilisateur)"""
    payload = {"email": "bob@example.com", "password": "mypassword"}

    # --- Test formulaire /signup ---
    r = client.post("/signup", data=payload, allow_redirects=False)
    assert r.status_code in (200, 303), f"Erreur signup HTML: {r.text}"

    # --- Test formulaire /login ---
    r2 = client.post("/login", data=payload)
    # la page peut rediriger vers /home ou afficher le token
    assert r2.status_code in (200, 303), f"Erreur login HTML: {r2.text}"
    assert "html" in r2.headers.get("content-type", ""), "La réponse devrait être du HTML"


def test_healthcheck():
    """Teste la route de santé /health"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
