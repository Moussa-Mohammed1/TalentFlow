from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class DepartmentSkills(Base):
    __tablename__ = 'department_skills'

    id = Column(Integer, primary_key=True, index=True)

    candidat_id = Column(Integer, ForeignKey("departments.id"), nullable=False)