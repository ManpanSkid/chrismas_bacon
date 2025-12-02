from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.schema import Base

DATABASE_URL = "sqlite:///./orders.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Get database session as context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()