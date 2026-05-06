import pytest

from app.payments.catalog import PaymentCatalog
from app.services.exceptions import PaymentTariffNotFoundError


@pytest.mark.unit
def test_payment_catalog_returns_tariffs() -> None:
    catalog = PaymentCatalog()

    tariffs = catalog.list_tariffs()

    assert len(tariffs) > 0


@pytest.mark.unit
def test_payment_catalog_returns_existing_tariff() -> None:
    catalog = PaymentCatalog()

    tariff = catalog.get_tariff("credits_50_manual")

    assert tariff.id == "credits_50_manual"
    assert tariff.credits == 50
    assert tariff.provider == "manual"


@pytest.mark.unit
def test_payment_catalog_rejects_unknown_tariff() -> None:
    catalog = PaymentCatalog()

    with pytest.raises(PaymentTariffNotFoundError):
        catalog.get_tariff("unknown_tariff")