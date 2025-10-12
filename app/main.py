import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from . import models, schemas, auth
from .database import SessionLocal, init_db


app = FastAPI()




@app.on_event("startup")
def on_startup():
init_db()




# Dependency
def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()




@app.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
# check exists
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




@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
db_user = db.query(models.User).filter(models.User.email == user.email).first()
if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
raise HTTPException(status_code=401, detail="Incorrect email or password")
token = auth.create_access_token({"sub": db_user.email})
return {"access_token": token, "token_type": "bearer"}




@app.get("/health")
def health():
return JSONResponse({"status": "ok"})
