from app.ai.adapters.nanobanano import NanoBananoAdapter
from app.ai.adapters.veo import VeoAdapter
from app.ai.base import AIAdapter
from app.services.exceptions import AIProviderNotFoundError


class AIRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, AIAdapter] = {
            NanoBananoAdapter.provider_name: NanoBananoAdapter(),
            VeoAdapter.provider_name: VeoAdapter(),
        }

    def get_adapter(
        self,
        provider_name: str,
    ) -> AIAdapter:
        adapter = self._adapters.get(provider_name)

        if adapter is None:
            raise AIProviderNotFoundError

        return adapter