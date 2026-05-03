import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GenerationImageRole(str, enum.Enum):
    INPUT = "input"
    OUTPUT = "output"


class GenerationImage(Base):
    __tablename__ = "generation_images"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    generation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[GenerationImageRole] = mapped_column(
        Enum(GenerationImageRole, name="generation_image_role"),
        nullable=False,
        index=True,
    )

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    telegram_file_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )