from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from src.db.database import Base
from enum import Enum


class StatusEnum(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"
    failed = "failed"

class File(Base):
    __tablename__ = "file"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    filename: Mapped[str] = mapped_column(String)
    content_type: Mapped[str]
    size: Mapped[int]
    status: Mapped[str] = mapped_column(SAEnum(StatusEnum, name='status_enum'),
                                        default=StatusEnum.uploaded)
    progress: Mapped[int] = mapped_column(default=0)
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    s3_path: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None]
