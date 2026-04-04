from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlalchemy.sql import func

class TimestampModel(SQLModel):
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False
    )
    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        },
        nullable=False
    )