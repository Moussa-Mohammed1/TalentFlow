from sqlalchemy import Integer, String, DateTime, Column
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    fullname = Column(String , nullable=False)

    email = Column(String, nullable=False, unique=True, index=True)
    
    password = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

