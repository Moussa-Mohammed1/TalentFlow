from sqlalchemy import Column, Integer, String
from app.core.database import Base

class SkillsCategory(Base):
    __tablename__ = "skills_category"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    