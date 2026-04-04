from typing import Annotated, List
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.exceptions.auth import AuthenticationError, ForbiddenError
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import TokenData, UserRole

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(reusable_oauth2)]
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token: missing subject")
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        raise AuthenticationError("Could not validate credentials.")

    user_repo = UserRepository(User, db)
    user = await user_repo.get(id=token_data.user_id)
    
    if not user:
        raise AuthenticationError("User not found.")
    if not user.is_active:
        raise AuthenticationError("User account is deactivated.")

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenError(
                message=f"Role '{current_user.role}' does not have enough permissions."
            )
        return current_user

allow_admin = RoleChecker([UserRole.ADMIN])
allow_analyst = RoleChecker([UserRole.ADMIN, UserRole.ANALYST])
allow_all = RoleChecker([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER])