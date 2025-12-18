import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.schema import Base

# -----------------------------
# Source DB (SQLite)
# -----------------------------
SQLITE_DATABASE_URL = "sqlite:///./orders.db"

sqlite_engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SQLiteSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sqlite_engine
)

# -----------------------------
# Target DB (PostgreSQL)
# -----------------------------
POSTGRES_DATABASE_URL = os.getenv("DATABASE_URL")

postgres_engine = create_engine(
    POSTGRES_DATABASE_URL,
    pool_pre_ping=True
)

PostgresSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=postgres_engine
)

# -----------------------------
# Init PostgreSQL ONLY
# -----------------------------
def init_db():
    Base.metadata.create_all(bind=postgres_engine)

# -----------------------------
# Dependencies
# -----------------------------
@contextmanager
def get_sqlite_db():
    db = SQLiteSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()
