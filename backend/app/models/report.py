import uuid
from sqlalchemy import Column, String, JSON, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    # 1. Primary Key: A unique ID for every report (e.g., 'rep_12345')
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # 2. User ID: To know which patient this belongs to
    user_id = Column(String, index=True)
    
    # 3. Basic Info
    filename = Column(String)
    
    # 4. The "Brain" Data (Text can be huge, so we use Text type, not String)
    extracted_text = Column(Text)
    
    # 5. The "Structured" Data (JSON is best for list of diseases/values)
    detected_entities = Column(JSON) # e.g. {"diseases": ["cancer"], "meds": []}
    extracted_values = Column(JSON)  # e.g. {"glucose": "150", "bp": "120/80"}
    
    # 6. Risk Score: 0.0 to 100.0
    risk_score = Column(Float, nullable=True)
    
    # 7. Timestamp: When was this uploaded?
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report_type = Column(String, default="General")