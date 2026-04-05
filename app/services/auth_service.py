import logging
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError

from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from app.core.config import settings
from app.core.exceptions.auth import AuthenticationError, ForbiddenError
from app.core.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserUpdate, UserRole

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(User, db)

    async def register_user(self, user_in: UserCreate) -> User:
        logger.info(f"Registering new user: {user_in.email}")
        
        existing_user = await self.user_repo.get_by_email(email=user_in.email)
        if existing_user:
            logger.warning(f"Registration blocked: {user_in.email} already exists.")
            raise UserAlreadyExistsError()

        # Decision: First user is Admin, everyone else is Viewer by default
        user_count = await self.user_repo.get_count()
        if user_count == 0:
            user_in.role = UserRole.ADMIN
            logger.info(f"Bootstrap: Assigning ADMIN role to the first user: {user_in.email}")
        else:
            user_in.role = UserRole.VIEWER

        try:
            hashed_pw = get_password_hash(user_in.password)
            new_user = self.user_repo.add(user_in, hashed_password=hashed_pw)
            await self.db.commit()
            await self.db.refresh(new_user)
            logger.info(f"User {user_in.email} successfully onboarded with role {new_user.role}")
            return new_user
        except IntegrityError:
            await self.db.rollback()
            logger.error(f"Integrity conflict for {user_in.email} during registration.")
            raise UserAlreadyExistsError()

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        logger.info(f"Login attempt: {login_data.email}")
        
        user = await self.user_repo.get_by_email(email=login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Invalid login for {login_data.email}")
            raise AuthenticationError("Invalid email or password")
        
        # Include 'role' in token claims for RBAC enforcement
        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        await self.user_repo.add_refresh_token(user_id=user.id, token=refresh_token)
        await self.db.commit()

        logger.info(f"User {user.id} logged in successfully with role {user.role}.")
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def rotate_tokens(self, refresh_token: str) -> Token:
        logger.info("Initiating token rotation cycle.")
        try:
            payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            role: str = payload.get("role")
            if not user_id:
                raise AuthenticationError("Invalid refresh token.")
        except JWTError:
            logger.warning("Expired or corrupted refresh token received.")
            raise AuthenticationError("Refresh token expired or invalid.")

        user = await self.user_repo.get_refresh_token(user_id=int(user_id), token=refresh_token)
        if not user:
            logger.error(f"Potential Token Replay Attack! Revoking access for user_id: {user_id}")
            raise AuthenticationError("Token has been revoked or already used.")

        # Re-include 'role' during rotation
        token_data = {"sub": str(user.id), "role": user.role}
        new_access = create_access_token(data=token_data)
        new_refresh = create_refresh_token(data=token_data)

        await self.user_repo.add_refresh_token(user_id=int(user_id), token=new_refresh)
        await self.db.commit()

        logger.info(f"Successful token rotation for user_id: {user_id}")
        return Token(access_token=new_access, refresh_token=new_refresh, token_type="bearer")

    # User Management for Admins
    async def get_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        return await self.user_repo.get_multi(skip=skip, limit=limit)

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get(id=user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        db_user = await self.user_repo.get(id=user_id)
        if not db_user:
            raise UserNotFoundError()
        
        if user_id == 1:
            if (user_in.role and user_in.role != db_user.role) or (user_in.is_active is False):
                logger.warning(f"Protected Action: Modification of bootstrap Admin (ID 1) blocked.")
                raise ForbiddenError("Modification of the primary system administrator is restricted.")

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        updated_user = self.user_repo.apply_update(db_user, update_data)
        await self.db.commit()
        await self.db.refresh(updated_user)
        return updated_user
