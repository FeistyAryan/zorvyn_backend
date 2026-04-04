from fastapi import APIRouter
from app.api.v1.endpoints import auth, financial_records, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(financial_records.router, prefix="/finance", tags=["Financial Records"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
