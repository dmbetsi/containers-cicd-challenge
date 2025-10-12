- FastAPI app with signup/login (bcrypt + JWT)
- Unit tests (pytest)
- Dockerfile + docker-compose (FastAPI + Postgres)
- GitHub Actions workflow that runs tests then builds & runs containers


## Quick start


1. Copy `.env.example` to `.env` and set values (especially `SECRET_KEY`).
2. Start services:


```bash
docker compose up --build

App will be at http://localhost:8000.

Running tests

pip install -r requirements.txt
pytest

Tests use an in-memory SQLite DB so they run quickly without Postgres.)

CI/CD (GitHub Actions)

.github/workflows/ci.yml runs on push to main and on PRs.

It runs pytest (unit tests) first.

Then it builds Docker image and runs docker compose up --build -d.

Secrets to configure in GitHub repository settings (Settings → Secrets & variables → Actions):

POSTGRES_USER

POSTGRES_PASSWORD

POSTGRES_DB

SECRET_KEY

Optional: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN (if you want to push image)

Notes & Security

Do not commit real secrets. Use GitHub Actions secrets.

DATABASE_URL is provided via environment variables; no credentials are hard-coded.
## Next steps


Open the canvas file above — it contains all project files in one place. You can copy them into a fresh repository and follow the README to run locally or in CI.
