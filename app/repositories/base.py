from typing import Generic, Type, TypeVar, Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=Any)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=Any)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: Any, include_deleted: bool = False) -> ModelType | None:
        statement = select(self.model).where(self.model.id == id)
        
        if hasattr(self.model, "is_deleted") and not include_deleted:
            statement = statement.where(self.model.is_deleted == False)
            
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        include_deleted: bool = False,
        **filters
    ) -> Sequence[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        
        if hasattr(self.model, "is_deleted") and not include_deleted:
            statement = statement.where(self.model.is_deleted == False)

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                statement = statement.where(getattr(self.model, field) == value)

        result = await self.db_session.execute(statement)
        return result.scalars().all()

    async def get_by(self, include_deleted: bool = False, **filters) -> ModelType | None:
        statement = select(self.model)
        
        if hasattr(self.model, "is_deleted") and not include_deleted:
            statement = statement.where(self.model.is_deleted == False)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
                
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()

    def add(self, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        obj_in_data = obj_in.model_dump()
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        return db_obj

    def apply_update(
        self, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        
        protected_fields = {"id", "created_at", "updated_at"} 
        
        for field in update_data:
            if hasattr(db_obj, field) and field not in protected_fields:
                setattr(db_obj, field, update_data[field])
        
        self.db_session.add(db_obj)
        return db_obj

    async def soft_delete(self, db_obj: ModelType) -> ModelType:
        if hasattr(db_obj, "is_deleted"):
            setattr(db_obj, "is_deleted", True)
        self.db_session.add(db_obj)
        return db_obj
