from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from datetime import datetime
from app.core.database import Base

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=True)
    