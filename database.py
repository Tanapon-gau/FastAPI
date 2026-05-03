import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb"
)
print(f"Connecting to database at {DATABASE_URL}")  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
