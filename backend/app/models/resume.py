from datetime import datetime
from sqlalchemy import String, Column, Integer, DateTime
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    path = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)