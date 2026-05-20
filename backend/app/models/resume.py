from sqlalchemy import String, Column, Integer, DateTime
from app.core.database import Base
from datetime import datetime

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    path = Column(String, nullable=False)

    created_at = Column(DateTime, datetime.utcnow)