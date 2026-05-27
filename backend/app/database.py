from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL load karein
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Engine create karein (Communication point)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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