from sqlalchemy import Column, Integer, DateTime, Text, String
from app.core.database import Base
from datetime import datetime

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=True)

    description = Column(Text, nullable=True)

    start_date = Column(DateTime, nullable=False)

    end_date = Column(DateTime, nullable=True)

