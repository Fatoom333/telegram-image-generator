from dataclasses import dataclass

from app.services.exceptions import AIModelNotFoundError


@dataclass(frozen=True)
class AIModel:
    provider: str
    model_name: str
    title: str
    cost_credits: int
    image_cost_credits: int
    max_input_images: int


class ModelCatalog:
    def __init__(self) -> None:

        self._models: dict[tuple[str, str], AIModel] = {
            ("nanobanano", "gemini-2.5-flash-image"): AIModel(
                provider="nanobanano",
                model_name="gemini-2.5-flash-image",
                title="NanoBanano",
                cost_credits=1,
                image_cost_credits=10,
                max_input_images=4,
            ),
            ("nanobanano", "gemini-3.1-flash-image-preview"): AIModel(
                provider="nanobanano",
                model_name="gemini-3.1-flash-image-preview",
                title="NanoBanano 2",
                cost_credits=2,
                image_cost_credits=20,
                max_input_images=4,
            ),
            ("nanobanano", "gemini-3-pro-image-preview"): AIModel(
                provider="nanobanano",
                model_name="gemini-3-pro-image-preview",
                title="NanoBanano Pro",
                cost_credits=3,
                image_cost_credits=40,
                max_input_images=4,
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
        input_images_cnt: int,
    ) -> int:
        model = self.get_model(
            provider=provider,
            model_name=model_name,
        )

        if input_images_cnt > model.max_input_images:
            raise AIModelNotFoundError

        if input_images_cnt > 0:
            return model.image_cost_credits

        return model.cost_credits