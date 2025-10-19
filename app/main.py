import os
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models, schemas, auth
from .database import SessionLocal, init_db


app = FastAPI(title="FastAPI Auth Interface")

# --- Configuration des templates et fichiers statiques ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


# --- Dependency pour la DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------
# 🔹 ROUTES HTML (interface utilisateur)
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": "Email déjà enregistré."}
        )

    hashed = auth.get_password_hash(password)
    db_user = models.User(email=email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if not db_user or not auth.verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Email ou mot de passe incorrect."}
        )
    token = auth.create_access_token({"sub": db_user.email})
    response = templates.TemplateResponse(
        "home.html",
        {"request": request, "message": f"Bienvenue, {db_user.email}!", "token": token},
    )
    return response


# -------------------------------------------------------------------
# 🔹 ROUTES API JSON (pour les tests et les clients REST)
# -------------------------------------------------------------------

@app.post("/api/signup", response_model=schemas.Token)
def api_signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Inscription via API JSON"""
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/login", response_model=schemas.Token)
def api_login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Connexion via API JSON"""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


# -------------------------------------------------------------------
# 🔹 HEALTH CHECK
# -------------------------------------------------------------------
@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})
