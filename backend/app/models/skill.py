from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Skill(Base):
	__tablename__ = "skills"

	id = Column(Integer, primary_key=True, index=True)
	
	name = Column(String, nullable=False, unique=True, index=True)
	
	created_at = Column(DateTime, default=datetime.utcnow)

