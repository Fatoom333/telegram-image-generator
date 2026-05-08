from dataclasses import dataclass

from app.services.exceptions import PaymentTariffNotFoundError


@dataclass(frozen=True)
class PaymentTariff:
    id: str
    title: str
    amount_rub: int
    credits: int


def make_tariff(
    *,
    title: str,
    amount_rub: int,
    credits: int,
) -> PaymentTariff:
    return PaymentTariff(
        id=f"credits_{credits}",
        title=title,
        amount_rub=amount_rub,
        credits=credits,
    )


class PaymentCatalog:
    def __init__(self) -> None:
        tariffs = [
            make_tariff(
                title="Start",
                amount_rub=99,
                credits=150,
            ),
            make_tariff(
                title="Base",
                amount_rub=199,
                credits=330,
            ),
            make_tariff(
                title="Popular",
                amount_rub=399,
                credits=750,
            ),
            make_tariff(
                title="Advanced",
                amount_rub=799,
                credits=1650,
            ),
            make_tariff(
                title="Maximum",
                amount_rub=1490,
                credits=3200,
            ),
        ]

        self._tariffs: dict[str, PaymentTariff] = {
            tariff.id: tariff
            for tariff in tariffs
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