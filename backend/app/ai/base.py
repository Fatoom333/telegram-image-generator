from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GenerateImageInput:
    generation_id: UUID
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
