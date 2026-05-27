import uuid
from sqlalchemy import Column, String, DateTime , Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # --- NEW PROFESSIONAL COLUMNS ---
    is_verified = Column(Boolean, default=False) # Verification check
    verification_token = Column(String, nullable=True) # For email link
    reset_token = Column(String, nullable=True) # For forgot password


    created_at = Column(DateTime(timezone=True), server_default=func.now())