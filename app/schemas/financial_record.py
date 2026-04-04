from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.core.enums import TransactionType, TransactionCategory

class FinancialRecordBase(BaseModel):
    amount: Decimal = Field(..., max_digits=15, decimal_places=2, gt=0)
    type: TransactionType
    category: TransactionCategory
    description: str | None = None
    date: datetime | None = None

class FinancialRecordCreate(FinancialRecordBase):
    pass

class FinancialRecordUpdate(BaseModel):
    amount: Decimal | None = Field(None, max_digits=15, decimal_places=2, gt=0)
    type: TransactionType | None = None
    category: TransactionCategory | None = None
    description: str | None = None
    date: datetime | None = None

class FinancialRecordRead(FinancialRecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DashboardSummary(BaseModel):
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_balance: Decimal = Decimal("0.00")
    category_breakdown: dict[str, Decimal] = {}