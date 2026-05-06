from app.ai.base import AIAdapter, GenerateImageInput, GenerateImageResult
from app.core.config import settings


class NanoBananoAdapter(AIAdapter):
    provider_name = "nanobanano"

    def __init__(self) -> None:
        self._api_key = settings.nanobanano_api_key

    async def generate_image(
        self,
        data: GenerateImageInput,
    ) -> GenerateImageResult:
        # TODO: позже здесь будет реальный запрос к NanoBanano API.
        raise NotImplementedError("NanoBanano adapter is not implemented yet")
