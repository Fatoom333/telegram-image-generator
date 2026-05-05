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
        # Здесь хранится список моделей, доступных пользователю.
        #
        # Как добавить новую модель:
        # 1. Добавь новую запись в self._models.
        # 2. Ключ должен быть tuple: (provider, model_name).
        # 3. provider должен совпадать с provider_name нужного AIAdapter.
        # 4. model_name должен быть тем именем модели, которое понимает adapter.
        # 5. Укажи стоимость генерации и лимит input images.
        #
        # Пример:
        # ("replicate", "flux-schnell"): AIModel(
        #     provider="replicate",
        #     model_name="flux-schnell",
        #     title="Flux Schnell",
        #     cost_credits=1,
        #     image_cost_credits=2,
        #     max_input_images=4,
        # )
        self._models: dict[tuple[str, str], AIModel] = {
            ("nanobanano", "nanobanano-v1"): AIModel(
                provider="nanobanano",
                model_name="nanobanano-v1",
                title="NanoBanano v1",
                cost_credits=1,
                image_cost_credits=2,
                max_input_images=4,
            ),
        }

        # Модель по умолчанию для MVP.
        # Если frontend не передал provider/model_name,
        # GenerationService возьмёт именно эту модель.
        #
        # Чтобы поменять дефолтную модель, укажи другой ключ из self._models.
        self._default_model = self._models[("nanobanano", "nanobanano-v1")]

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