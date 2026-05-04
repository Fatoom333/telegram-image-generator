from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateImageInput:
    prompt: str
    input_image_paths: list[str]
    model_name: str


@dataclass(frozen=True)
class GenerateImageResult:
    output_image_paths: list[str]
    provider_generation_id: str | None = None


class AIAdapter(ABC):
    provider_name: str

    @abstractmethod
    async def generate_image(
        self,
        data: GenerateImageInput,
    ) -> GenerateImageResult:
        pass
