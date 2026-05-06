from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePaymentInput:
    purchase_id: UUID
    telegram_id: int
    amount_rub: int
    credits: int
    description: str


@dataclass(frozen=True)
class CreatePaymentResult:
    provider_payment_id: str | None
    payment_url: str | None


class PaymentAdapter(ABC):
    provider_name: str

    @abstractmethod
    async def create_payment(
        self,
        data: CreatePaymentInput,
    ) -> CreatePaymentResult:
        pass
