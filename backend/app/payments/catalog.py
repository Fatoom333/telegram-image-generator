
from dataclasses import dataclass

from app.services.exceptions import PaymentTariffNotFoundError


@dataclass(frozen=True)
class PaymentTariff:
    id: str
    title: str
    amount_rub: int
    credits: int
    provider: str


class PaymentCatalog:
    def __init__(self) -> None:
        # Здесь хранятся доступные тарифы.
        #
        # Как добавить новый тариф:
        # 1. Добавь новую запись в self._tariffs.
        # 2. id должен быть стабильным, потому что frontend будет отправлять его в backend.
        # 3. provider должен совпадать с provider_name одного из PaymentAdapter.
        # 4. amount_rub — цена.
        # 5. credits — сколько кредитов получает пользователь.
        #
        # Пример для будущего СБП:
        # "credits_100_sbp": PaymentTariff(
        #     id="credits_100_sbp",
        #     title="100 credits",
        #     amount_rub=199,
        #     credits=100,
        #     provider="sbp",
        # )
        self._tariffs: dict[str, PaymentTariff] = {
            "credits_50_manual": PaymentTariff(
                id="credits_50_manual",
                title="50 credits",
                amount_rub=99,
                credits=50,
                provider="manual",
            ),
            "credits_100_lava": PaymentTariff(
                id="credits_100_lava",
                title="100 credits",
                amount_rub=199,
                credits=100,
                provider="lava",
            ),
        }

    def get_tariff(
        self,
        tariff_id: str,
    ) -> PaymentTariff:
        tariff = self._tariffs.get(tariff_id)

        if tariff is None:
            raise PaymentTariffNotFoundError

        return tariff

    def list_tariffs(self) -> list[PaymentTariff]:
        return list(self._tariffs.values())