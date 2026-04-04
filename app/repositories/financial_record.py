from typing import Sequence
from sqlalchemy import select, func, and_
from app.repositories.base import BaseRepository
from app.models.financial_record import FinancialRecord
from app.schemas.financial_record import FinancialRecordCreate, FinancialRecordUpdate, DashboardSummary
from app.core.enums import TransactionType
from decimal import Decimal
from datetime import datetime

class FinancialRecordRepository(BaseRepository[FinancialRecord, FinancialRecordCreate, FinancialRecordUpdate]):
    async def get_summary(self, user_id: int) -> DashboardSummary:
        statement = select(
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total")
        ).where(
            FinancialRecord.user_id == user_id,
            FinancialRecord.is_deleted == False
        ).group_by(FinancialRecord.type)
        
        result = await self.db_session.execute(statement)
        rows = result.all()
        
        summary = DashboardSummary()
        for row in rows:
            if row.type == TransactionType.INCOME:
                summary.total_income = row.total or Decimal("0.00")
            else:
                summary.total_expense = row.total or Decimal("0.00")
        
        summary.net_balance = summary.total_income - summary.total_expense
        
        cat_statement = select(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total")
        ).where(
            FinancialRecord.user_id == user_id,
            FinancialRecord.is_deleted == False
        ).group_by(FinancialRecord.category)
        
        cat_result = await self.db_session.execute(cat_statement)
        cat_rows = cat_result.all()
        
        summary.category_breakdown = {row.category.value: row.total for row in cat_rows}
        
        return summary

    async def get_filtered_records(
        self,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> Sequence[FinancialRecord]:
        statement = select(FinancialRecord).where(
            FinancialRecord.user_id == user_id,
            FinancialRecord.is_deleted == False
        ).order_by(FinancialRecord.date.desc())

        if category:
            statement = statement.where(FinancialRecord.category == category)
        if type:
            statement = statement.where(FinancialRecord.type == type)
        if start_date:
            statement = statement.where(FinancialRecord.date >= start_date)
        if end_date:
            statement = statement.where(FinancialRecord.date <= end_date)

        statement = statement.offset(skip).limit(limit)
        result = await self.db_session.execute(statement)
        return result.scalars().all()
