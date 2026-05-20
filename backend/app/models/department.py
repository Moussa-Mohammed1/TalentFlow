from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base


class Department(Base):
	__tablename__ = "departments"

	id = Column(Integer, primary_key=True, index=True)

	name = Column(String, nullable=False, unique=True, index=True)

	required_exp_years = Column(Integer, nullable=False)

	created_at = Column(DateTime, default=datetime.utcnow)