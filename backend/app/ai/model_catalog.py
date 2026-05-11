from dataclasses import dataclass

from app.services.exceptions import AIModelNotFoundError


@dataclass(frozen=True)
class AIModel:
    provider: str
    model_name: str
    title: str
    output_asset_type: str
    cost_credits: int
    reference_cost_credits: int
    max_input_assets: int


class ModelCatalog:
    def __init__(self) -> None:
        self._models: dict[tuple[str, str], AIModel] = {
            ("nanobanano", "gemini-2.5-flash-image"): AIModel(
                provider="nanobanano",
                model_name="gemini-2.5-flash-image",
                title="NanoBanano",
                output_asset_type="image",
                cost_credits=10,
                reference_cost_credits=1,
                max_input_assets=4,
            ),
            ("nanobanano", "gemini-3.1-flash-image-preview"): AIModel(
                provider="nanobanano",
                model_name="gemini-3.1-flash-image-preview",
                title="NanoBanano 2",
                output_asset_type="image",
                cost_credits=20,
                reference_cost_credits=1,
                max_input_assets=4,
            ),
            ("nanobanano", "gemini-3-pro-image-preview"): AIModel(
                provider="nanobanano",
                model_name="gemini-3-pro-image-preview",
                title="NanoBanano Pro",
                output_asset_type="image",
                cost_credits=40,
                reference_cost_credits=2,
                max_input_assets=4,
            ),
            ("veo", "veo-3.1-fast-generate-001"): AIModel(
                provider="veo",
                model_name="veo-3.1-fast-generate-001",
                title="Veo 3.1 Fast",
                output_asset_type="video",
                cost_credits=250,
                reference_cost_credits=30,
                max_input_assets=3,
            ),
            ("veo", "veo-3.1-generate-001"): AIModel(
                provider="veo",
                model_name="veo-3.1-generate-001",
                title="Veo 3.1",
                output_asset_type="video",
                cost_credits=900,
                reference_cost_credits=100,
                max_input_assets=3,
            ),
        }

        self._default_model = self._models[("nanobanano", "gemini-2.5-flash-image")]

    def get_default_model(self) -> AIModel:
        return self._default_model

    def get_model(
            self,
            provider: str,
            model_name: str,
    ) -> AIModel:
        model = self._models.get((provider, model_name))

        if model is None:
            raise AIModelNotFoundError

        return model

    def list_models(self) -> list[AIModel]:
        return list(self._models.values())

    def calculate_cost(
            self,
            provider: str,
            model_name: str,
            input_assets_cnt: int,
    ) -> int:
        model = self.get_model(
            provider=provider,
            model_name=model_name,
        )

        if input_assets_cnt > model.max_input_assets:
            raise AIModelNotFoundError

        if input_assets_cnt > 0:
            return model.reference_cost_credits

        return model.cost_credits
