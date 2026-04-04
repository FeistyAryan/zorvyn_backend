import logging
from typing import Sequence
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.financial_record import FinancialRecordRepository
from app.repositories.audit import AuditRepository
from app.models.financial_record import FinancialRecord
from app.schemas.financial_record import FinancialRecordCreate, FinancialRecordRead, FinancialRecordUpdate, DashboardSummary
from app.schemas.audit import AuditCreate
from app.core.exceptions.financial_record import (
    RecordNotFoundError, 
    InvalidTransactionError
)
from app.core.enums import AuditAction
from app.core.db import AsyncSessionLocal 
from datetime import datetime

logger = logging.getLogger(__name__)

class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.financial_repo = FinancialRecordRepository(FinancialRecord, db)
        self.audit_repo = AuditRepository(db)

    async def _create_audit_log(self, audit_data: AuditCreate):
        async with AsyncSessionLocal() as new_session:
            try:
                local_audit_repo = AuditRepository(new_session)
                local_audit_repo.add(audit_data)
                await new_session.commit()
                logger.info(f"Audit log saved: {audit_data.action} on {audit_data.target_entity_id}")
            except Exception as e:
                logger.error(f"Background audit failed: {str(e)}")

    async def _get_and_verify_record(self, record_id: int, user_id: int) -> FinancialRecord:
        record = await self.financial_repo.get(id=record_id)
        
        if not record or record.user_id != user_id:
            logger.warning(f"Verification Failed: User {user_id} -> Record {record_id}")
            raise RecordNotFoundError()
        return record

    async def get_filtered_records(
        self,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        category: str | None = None,
        type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> Sequence[FinancialRecord]:
        logger.info(f"Fetching filtered records for user {user_id}")
        return await self.financial_repo.get_filtered_records(
            user_id=user_id,
            skip=skip,
            limit=limit,
            category=category,
            type=type,
            start_date=start_date,
            end_date=end_date
        )

    async def get_dashboard_summary(self, user_id: int) -> DashboardSummary:
        logger.info(f"Generating dashboard summary for user {user_id}")
        return await self.financial_repo.get_summary(user_id=user_id)

    async def create_record(
        self, 
        record_in: FinancialRecordCreate, 
        user_id: int, 
        bg_tasks: BackgroundTasks
    ) -> FinancialRecord:
        logger.info(f"User {user_id} initiating record creation.")
        
        if record_in.amount <= 0:
            raise InvalidTransactionError("Transaction amount must be greater than zero.")

        extra_data = {"user_id": user_id}
        if not record_in.date:
            extra_data["date"] = datetime.now()

        db_record = self.financial_repo.add(record_in, **extra_data)
        await self.db.flush()

        audit_data = AuditCreate(
            action=AuditAction.CREATE,
            target_entity="FinancialRecord",
            target_entity_id=db_record.id,
            executor_id=user_id,
            payload=record_in.model_dump()
        )
        
        bg_tasks.add_task(self._create_audit_log, audit_data)
        
        await self.db.commit()
        await self.db.refresh(db_record)
        return db_record

    async def update_record(
        self, 
        record_id: int, 
        record_in: FinancialRecordUpdate, 
        user_id: int,
        bg_tasks: BackgroundTasks
    ) -> FinancialRecord:
        logger.info(f"User {user_id} updating record {record_id}")
        
        db_record = await self._get_and_verify_record(record_id, user_id)
        
        if record_in.amount is not None and record_in.amount <= 0:
            raise InvalidTransactionError("Updated amount cannot be zero or negative.")

        updated_record = self.financial_repo.apply_update(db_record, record_in)

        audit_data = AuditCreate(
            action=AuditAction.UPDATE,
            target_entity="FinancialRecord",
            target_entity_id=record_id,
            executor_id=user_id,
            payload=record_in.model_dump(exclude_unset=True)
        )
        
        bg_tasks.add_task(self._create_audit_log, audit_data)

        await self.db.commit()
        await self.db.refresh(updated_record)
        return updated_record

    async def delete_record(self, record_id: int, user_id: int, bg_tasks: BackgroundTasks) -> bool:
        logger.info(f"User {user_id} soft-deleting record {record_id}")
        
        db_record = await self._get_and_verify_record(record_id, user_id)
        
        await self.financial_repo.soft_delete(db_record)

        audit_data = AuditCreate(
            action=AuditAction.DELETE,
            target_entity="FinancialRecord",
            target_entity_id=record_id,
            executor_id=user_id
        )
        
        bg_tasks.add_task(self._create_audit_log, audit_data)

        await self.db.commit()
        return True
