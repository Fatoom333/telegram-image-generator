import asyncio
import time

from google import genai
from google.genai import types

from app.ai.base import AIAdapter, GeneratedAsset, GenerateInput, GenerateResult
from app.core.config import settings
from app.storage.gcs import GCSStorageClient
from app.storage.local import LocalFileStorage


class VeoAdapter(AIAdapter):
    provider_name = "veo"

    _SUPPORTED_MODELS = {
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
    }

    def __init__(self) -> None:
        self._project_id = settings.veo_project_id
        self._location = settings.veo_location
        self._bucket = settings.veo_output_gcs_bucket
        self._prefix = settings.veo_output_gcs_prefix.strip("/")
        self._storage = LocalFileStorage()
        self._gcs = GCSStorageClient()

    async def generate(
            self,
            data: GenerateInput,
    ) -> GenerateResult:
        return await asyncio.to_thread(self._generate_sync, data)

    def _generate_sync(
            self,
            data: GenerateInput,
    ) -> GenerateResult:
        if data.model_name not in self._SUPPORTED_MODELS:
            raise ValueError(f"Unsupported Veo model: {data.model_name}")

        client = genai.Client(
            vertexai=True,
            project=self._project_id,
            location=self._location,
        )

        output_gcs_uri = self._build_output_gcs_uri(data)

        operation = client.models.generate_videos(
            model=data.model_name,
            prompt=data.prompt,
            image=self._build_input_image(data.input_asset_paths),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=8,
                aspect_ratio="16:9",
                enhance_prompt=True,
                output_gcs_uri=output_gcs_uri,
            ),
        )

        while not operation.done:
            time.sleep(20)
            operation = client.operations.get(operation)

        operation_response = getattr(operation, "response", None)
        if operation_response is None:
            operation_response = getattr(operation, "result", None)

        if operation_response is None or not operation_response.generated_videos:
            raise RuntimeError("Veo did not return generated videos")

        assets: list[GeneratedAsset] = []

        for index, generated_video in enumerate(operation_response.generated_videos, start=1):
            video_uri = generated_video.video.uri
            if video_uri is None:
                continue

            video_bytes = self._gcs.download_gcs_uri_as_bytes(video_uri)

            local_path = self._storage.save_generation_output_asset_bytes(
                generation_id=data.generation_id,
                asset_bytes=video_bytes,
                asset_type="video",
                mime_type="video/mp4",
                index=index,
            )

            assets.append(
                GeneratedAsset(
                    file_path=local_path,
                    asset_type="video",
                    mime_type="video/mp4",
                    gcs_uri=video_uri,
                )
            )

        if not assets:
            raise RuntimeError("Veo did not return downloadable video files")

        return GenerateResult(
            assets=assets,
            provider_generation_id=None,
        )

    def _build_output_gcs_uri(
            self,
            data: GenerateInput,
    ) -> str:
        return f"gs://{self._bucket}/{self._prefix}/{data.generation_id}/"

    def _build_input_image(
            self,
            input_asset_paths: list[str],
    ) -> types.Image | None:
        if not input_asset_paths:
            return None

        first_asset_path = self._storage.resolve_private_path(input_asset_paths[0])

        return types.Image.from_file(
            location=str(first_asset_path),
        )
