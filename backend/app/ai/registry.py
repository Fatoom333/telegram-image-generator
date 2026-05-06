from app.ai.adapters.nanobanano import NanoBananoAdapter
from app.ai.base import AIAdapter
from app.services.exceptions import AIProviderNotFoundError


class AIRegistry:
    def __init__(self) -> None:
        # Здесь регистрируются AI adapters.
        #
        # Как добавить нового провайдера:
        # 1. Создай новый adapter в app/ai/adapters/.
        #    Например: app/ai/adapters/replicate.py
        # 2. Adapter должен наследоваться от AIAdapter.
        # 3. У adapter должен быть provider_name.
        #    Например: provider_name = "replicate"
        # 4. Импортируй adapter здесь.
        # 5. Добавь его в словарь self._adapters.
        #
        # Важно:
        # provider_name должен совпадать с provider в ModelCatalog.
        self._adapters: dict[str, AIAdapter] = {
            NanoBananoAdapter.provider_name: NanoBananoAdapter(),

            # Пример будущего adapter:
            # ReplicateAdapter.provider_name: ReplicateAdapter(),
        }

    def get_adapter(
        self,
        provider_name: str,
    ) -> AIAdapter:
        adapter = self._adapters.get(provider_name)

        if adapter is None:
            raise AIProviderNotFoundError

        return adapter