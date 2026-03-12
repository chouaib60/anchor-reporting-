from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from schema.user import UserOut



class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TemplateVersionOut(BaseModel):
    id: UUID4
    version: int
    object_key: str
    is_active: bool
    created_at: datetime


class TemplateOut(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    created_by: UserOut
    created_at: datetime
    updated_at: datetime
    versions: list[TemplateVersionOut] = []