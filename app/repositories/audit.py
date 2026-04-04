from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.audit import AuditLog
from app.schemas.audit import AuditCreate, AuditUpdate

class AuditRepository(BaseRepository[AuditLog, AuditCreate, AuditUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=AuditLog, db_session=db_session)