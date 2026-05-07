import asyncio
from pathlib import Path

from google import genai
from google.genai import types

from app.ai.base import AIAdapter, GenerateImageInput, GenerateImageResult
from app.core.config import settings
from app.storage.local import LocalFileStorage


class NanoBananoAdapter(AIAdapter):
    provider_name = "nanobanano"

    _SUPPORTED_MODELS = {
        "gemini-2.5-flash-image",
        "gemini-3-pro-image-preview",
        "gemini-3.1-flash-image-preview",
    }

    _EXTENSION_TO_MIME_TYPE = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    def __init__(self) -> None:
        self._project_id = settings.nanobanano_project_id
        self._location = settings.nanobanano_location
        self._storage = LocalFileStorage()

    async def generate_image(
        self,
        data: GenerateImageInput,
    ) -> GenerateImageResult:
        return await asyncio.to_thread(self._generate_image_sync, data)

    def _generate_image_sync(
        self,
        data: GenerateImageInput,
    ) -> GenerateImageResult:
        if data.model_name not in self._SUPPORTED_MODELS:
            raise ValueError(f"Unsupported NanoBanano model: {data.model_name}")

        client = genai.Client(
            vertexai=True,
            project=self._project_id,
            location=self._location,
        )

        parts: list[types.Part] = []

        for input_image_path in data.input_image_paths:
            private_path = self._storage.resolve_private_path(input_image_path)
            parts.append(
                types.Part.from_bytes(
                    data=private_path.read_bytes(),
                    mime_type=self._detect_mime_type(private_path),
                )
            )

        parts.append(types.Part.from_text(text=data.prompt))

        response = client.models.generate_content(
            model=data.model_name,
            contents=[
                types.Content(
                    role="user",
                    parts=parts,
                )
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        output_image_paths: list[str] = []
        image_index = 1

        for candidate in response.candidates or []:
            if candidate.content is None:
                continue

            for part in candidate.content.parts or []:
                inline_data = part.inline_data
                if inline_data is None or inline_data.data is None:
                    continue

                mime_type = inline_data.mime_type or "image/png"

                relative_path = self._storage.save_generation_output_image_bytes(
                    generation_id=data.generation_id,
                    image_bytes=inline_data.data,
                    mime_type=mime_type,
                    index=image_index,
                )
                output_image_paths.append(relative_path)
                image_index += 1

        if not output_image_paths:
            raise RuntimeError("NanoBanano did not return any output images")

        return GenerateImageResult(
            output_image_paths=output_image_paths,
            provider_generation_id=None,
        )

    @classmethod
    def _detect_mime_type(cls, file_path: Path) -> str:
        mime_type = cls._EXTENSION_TO_MIME_TYPE.get(file_path.suffix.lower())
        if mime_type is None:
            raise ValueError(
                f"Unsupported input image extension: {file_path.suffix}",
            )
        return mime_type