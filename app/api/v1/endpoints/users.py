from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import allow_admin, CurrentUser
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserRead, UserUpdate
from app.core.limiter import limiter

router = APIRouter()

@router.get("/", response_model=List[UserRead])
@limiter.limit("20/minute")
async def get_all_users(
    request: Request,
    current_user: Annotated[CurrentUser, Depends(allow_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    auth_service = AuthService(db)
    return await auth_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
@limiter.limit("30/minute")
async def get_user_by_id(
    request: Request,
    user_id: int,
    current_user: Annotated[CurrentUser, Depends(allow_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    auth_service = AuthService(db)
    return await auth_service.get_user_by_id(user_id=user_id)

@router.patch("/{user_id}", response_model=UserRead)
@limiter.limit("10/minute")
async def update_user(
    request: Request,
    user_id: int,
    user_in: UserUpdate,
    current_user: Annotated[CurrentUser, Depends(allow_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    auth_service = AuthService(db)
    return await auth_service.update_user(user_id=user_id, user_in=user_in)
