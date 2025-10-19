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


# --- Page d'accueil ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# --- Page d'inscription ---
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


# --- Page de connexion ---
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


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})
