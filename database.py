import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("sqlite:///./"):
        db_name = database_url.removeprefix("sqlite:///./")
        DATABASE_URL = f"sqlite:///{(BASE_DIR / db_name).as_posix()}"
    else:
        DATABASE_URL = database_url
else:
    DATABASE_URL = f"sqlite:///{(BASE_DIR / 'routewise.db').as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
