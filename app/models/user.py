from sqlmodel import Field
from app.models.base import TimestampModel
from app.core.enums import UserRole

class User(TimestampModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.VIEWER)
    hashed_refresh_token: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False, index=True)