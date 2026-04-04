from fastapi import APIRouter, Depends, Query, status, BackgroundTasks, Request
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.v1.dependencies import allow_admin, allow_analyst, allow_all, CurrentUser
from app.core.db import get_db
from app.services.financial_service import FinanceService
from app.schemas.financial_record import (
    FinancialRecordCreate, 
    FinancialRecordRead, 
    FinancialRecordUpdate,
    DashboardSummary
)
from app.core.enums import TransactionType, TransactionCategory
from app.core.limiter import limiter

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
@limiter.limit("20/minute")
async def get_dashboard_summary(
    request: Request,
    current_user: Annotated[CurrentUser, Depends(allow_all)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    finance_service = FinanceService(db)
    return await finance_service.get_dashboard_summary(user_id=current_user.id)

@router.get("/all", response_model=List[FinancialRecordRead])
@limiter.limit("30/minute")
async def get_all_records(
    request: Request,
    current_user: Annotated[CurrentUser, Depends(allow_all)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: TransactionCategory | None = Query(None),
    type: TransactionType | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
):
    finance_service = FinanceService(db)
    return await finance_service.get_filtered_records(
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        category=category,
        type=type,
        start_date=start_date,
        end_date=end_date
    )

@router.post("/create", response_model=FinancialRecordRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_record(
    request: Request,
    record_in: FinancialRecordCreate,
    current_user: Annotated[CurrentUser, Depends(allow_analyst)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    finance_service = FinanceService(db)
    return await finance_service.create_record(
        record_in, 
        user_id=current_user.id, 
        bg_tasks=background_tasks
    )

@router.patch("/update/{record_id}", response_model=FinancialRecordRead)
@limiter.limit("10/minute")
async def update_record(
    request: Request,
    record_id: int,
    record_in: FinancialRecordUpdate,
    current_user: Annotated[CurrentUser, Depends(allow_analyst)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    finance_service = FinanceService(db)
    return await finance_service.update_record(
        record_id, 
        record_in, 
        user_id=current_user.id, 
        bg_tasks=background_tasks
    )

@router.delete("/delete/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_record(
    request: Request,
    record_id: int,
    current_user: Annotated[CurrentUser, Depends(allow_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    finance_service = FinanceService(db)
    await finance_service.delete_record(
        record_id, 
        user_id=current_user.id, 
        bg_tasks=background_tasks
    )
    return None
