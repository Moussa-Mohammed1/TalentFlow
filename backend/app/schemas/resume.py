from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeBase(BaseModel):
	path: str


class ResumeCreate(ResumeBase):
	pass


class ResumeRead(ResumeBase):
	id: int
	created_at: datetime | None = None

	model_config = ConfigDict(from_attributes=True)
