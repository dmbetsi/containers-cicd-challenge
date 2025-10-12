import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Handle shared in-memory SQLite for testing
    if ":memory:" in DATABASE_URL:
        DATABASE_URL = "sqlite:///file::memory:?cache=shared"

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool if "memory" in DATABASE_URL else None,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
