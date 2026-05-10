from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GenerateInput:
    generation_id: UUID
    prompt: str
    input_asset_paths: list[str]
    model_name: str


@dataclass(frozen=True)
class GeneratedAsset:
    file_path: str
    asset_type: str
    mime_type: str
    gcs_uri: str | None = None


@dataclass(frozen=True)
class GenerateResult:
    assets: list[GeneratedAsset]
    provider_generation_id: str | None = None


class AIAdapter(ABC):
    provider_name: str

    @abstractmethod
    async def generate(
            self,
            data: GenerateInput,
    ) -> GenerateResult:
        raise NotImplementedError
