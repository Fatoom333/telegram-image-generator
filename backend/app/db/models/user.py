from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.audit_log import AuditLog
    from app.db.models.credit_transaction import CreditTransaction
    from app.db.models.generation import Generation
    from app.db.models.purchase import Purchase
    from app.db.models.user_session import UserSession


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    free_generations_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    generations: Mapped[list[Generation]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    purchases: Mapped[list[Purchase]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    credit_transactions: Mapped[list[CreditTransaction]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    session: Mapped[UserSession | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


    audit_logs_as_actor: Mapped[list[AuditLog]] = relationship(
        back_populates="actor",
        foreign_keys="AuditLog.actor_telegram_id",
    )

    audit_logs_as_target: Mapped[list[AuditLog]] = relationship(
        back_populates="target",
        foreign_keys="AuditLog.target_telegram_id",
    )