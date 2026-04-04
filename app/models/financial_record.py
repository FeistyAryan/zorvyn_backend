from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, Relationship
from sqlalchemy import Column, DateTime, func
from app.models.base import TimestampModel
from app.core.enums import TransactionType, TransactionCategory

class FinancialRecord(TimestampModel, table=True):
    __tablename__ = "financial_record"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)
    amount: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    type: TransactionType = Field(nullable=False)
    category: TransactionCategory = Field(index=True, nullable=False)
    description: str | None = Field(default=None)
    date: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            nullable=False
        )
    )
    is_deleted: bool = Field(default=False, index=True)
