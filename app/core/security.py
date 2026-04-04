from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def _create_token(data: Dict[str, Any], expires_delta: timedelta, secret_key: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        secret_key, 
        algorithm=settings.ALGORITHM
    )

def create_access_token(data: Dict[str, Any]) -> str:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = data.copy()
    token_data.update({"type": "access"})
    return _create_token(token_data, expires, settings.SECRET_KEY)

def create_refresh_token(data: Dict[str, Any]) -> str:
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = data.copy()
    token_data.update({"type": "refresh"})
    return _create_token(token_data, expires, settings.REFRESH_SECRET_KEY)
