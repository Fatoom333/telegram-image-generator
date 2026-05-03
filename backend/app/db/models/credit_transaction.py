import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CreditTransactionType(str, enum.Enum):
    GRANT = "grant"
    SPEND = "spend"
    REFUND = "refund"
    PURCHASE = "purchase"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("generations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    type: Mapped[CreditTransactionType] = mapped_column(
        Enum(CreditTransactionType, name="credit_transaction_type"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)

    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )