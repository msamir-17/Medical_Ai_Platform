from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL load karein (fallback to sqlite in CI/testing if not provided)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./test.db"

# Engine create karein (Communication point with automatic reconnect pool)
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
engine_kwargs = {"pool_pre_ping": True}
if "sqlite" not in SQLALCHEMY_DATABASE_URL:
    engine_kwargs.update({"pool_recycle": 300, "pool_size": 10, "max_overflow": 20})

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Connection session banayein
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Saare models is Base ko inherit karenge
Base = declarative_base()

# Dependency: Har request ke liye naya connection khulega aur kaam ke baad band ho jayega
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()