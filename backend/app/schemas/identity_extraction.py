from __future__ import annotations

from pydantic import BaseModel, Field


class IdentityFieldRead(BaseModel):
    value: str | None = None
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)


class ResumeIdentityRead(BaseModel):
    name: IdentityFieldRead = Field(default_factory=IdentityFieldRead)
    email: IdentityFieldRead = Field(default_factory=IdentityFieldRead)
    phone: IdentityFieldRead = Field(default_factory=IdentityFieldRead)
