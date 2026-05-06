import pytest

from app.ai.model_catalog import ModelCatalog
from app.services.exceptions import AIModelNotFoundError


@pytest.mark.unit
def test_model_catalog_returns_default_model() -> None:
    catalog = ModelCatalog()

    model = catalog.get_default_model()

    assert model.provider == "nanobanano"
    assert model.model_name == "nanobanano-v1"
    assert model.max_input_images == 4


@pytest.mark.unit
def test_model_catalog_calculates_text_generation_cost() -> None:
    catalog = ModelCatalog()

    cost = catalog.calculate_cost(
        provider="nanobanano",
        model_name="nanobanano-v1",
        input_images_cnt=0,
    )

    assert cost == 1


@pytest.mark.unit
def test_model_catalog_calculates_image_generation_cost() -> None:
    catalog = ModelCatalog()

    cost = catalog.calculate_cost(
        provider="nanobanano",
        model_name="nanobanano-v1",
        input_images_cnt=2,
    )

    assert cost == 2


@pytest.mark.unit
def test_model_catalog_rejects_unknown_model() -> None:
    catalog = ModelCatalog()

    with pytest.raises(AIModelNotFoundError):
        catalog.get_model(
            provider="unknown",
            model_name="unknown-model",
        )