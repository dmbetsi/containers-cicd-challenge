import os

from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Use shared in-memory database if :memory: is used
    if DATABASE_URL.endswith(":memory:"):
        DATABASE_URL = "sqlite://"
        connect_args.update({"uri": True})
        DATABASE_URL = "sqlite:///file::memory:?cache=shared"

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool if "memory" in DATABASE_URL else None,
)
