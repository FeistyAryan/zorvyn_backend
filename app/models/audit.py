from datetime import datetime
from sqlalchemy import Column, JSON, DateTime
from sqlmodel import Field, SQLModel
from sqlalchemy.sql import func
from app.core.enums import AuditAction

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    id: int | None = Field(default=None, primary_key=True)
    action: AuditAction = Field(nullable=False)
    target_entity: str = Field(nullable=False)
    target_entity_id: int | None = Field(default=None)
    executor_id: int = Field(foreign_key="user.id", index=True)
    payload: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            nullable=False
        )
    )