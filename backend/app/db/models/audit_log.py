from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.db.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    actor_telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    target_telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    actor: Mapped[User | None] = relationship(
        back_populates="audit_logs_as_actor",
        foreign_keys=[actor_telegram_id],
    )

    target: Mapped[User | None] = relationship(
        back_populates="audit_logs_as_target",
        foreign_keys=[target_telegram_id],
    )