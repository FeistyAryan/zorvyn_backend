from fastapi import APIRouter, Depends, Request, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin, Token, UserCreate, UserRead
from app.core.limiter import limiter

router = APIRouter()

def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,   
        secure=True,     
        samesite="lax",  
        max_age=7 * 24 * 3600 
    )

@router.post("/register", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    login_data: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    tokens = await auth_service.authenticate_user(login_data)
    
    set_refresh_cookie(response, tokens.refresh_token)
    return tokens

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        from app.core.exceptions.auth import AuthenticationError
        raise AuthenticationError("Refresh token missing in cookies")
        
    auth_service = AuthService(db)
    new_tokens = await auth_service.rotate_tokens(refresh_token)
    
    set_refresh_cookie(response, new_tokens.refresh_token)
    return new_tokens
