from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by(email=email)

    async def create_user(self, user_in: UserCreate) -> User:
        db_obj = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_active=user_in.is_active
        )
        self.db_session.add(db_obj)
        return db_obj

    async def add_refresh_token(self, user_id: int, token: str) -> None:
        user = await self.get(id=user_id)
        if user:
            user.hashed_refresh_token = get_password_hash(token)
            self.db_session.add(user)

    async def get_refresh_token(self, user_id: int, token: str) -> User | None:
        user = await self.get(id=user_id)
        if user and user.hashed_refresh_token:
            if verify_password(token, user.hashed_refresh_token):
                return user
        return None

    async def delete_refresh_token(self, user_id: int) -> None:
        user = await self.get(id=user_id)
        if user:
            user.hashed_refresh_token = None
            self.db_session.add(user)
