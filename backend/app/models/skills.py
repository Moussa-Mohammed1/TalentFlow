from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class Skills(Base):

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    category_id = Column(Integer, ForeignKey("skills_category.id"), nullable=False)