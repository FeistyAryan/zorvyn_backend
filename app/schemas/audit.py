from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import AuditAction

class AuditBase(BaseModel):
    action: AuditAction
    target_entity: str
    target_entity_id: int | None = None
    executor_id: int
    payload: dict | None = None

class AuditCreate(AuditBase):
    pass

class AuditUpdate(BaseModel):
    pass

class AuditLogRead(AuditBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
