import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Override vía env var para poder apuntar los tests a una base temporal en vez
# de la de desarrollo (ver backend/tests/testing_setup.py).
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evaluador.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()