import asyncio
import logging
import mimetypes
import time
from collections.abc import Iterable
from pathlib import Path

from google import genai
from google.genai import types

from app.ai.base import AIAdapter, GeneratedAsset, GenerateInput, GenerateResult
from app.core.config import settings
from app.storage.gcs import GCSStorageClient
from app.storage.local import LocalFileStorage

logger = logging.getLogger(__name__)


class VeoAdapter(AIAdapter):
    provider_name = "veo"

    _SUPPORTED_MODELS = {
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
    }

    _SUPPORTED_REFERENCE_MIME_TYPES = {
        "image/jpeg",
        "image/png",
    }

    _MAX_REFERENCE_IMAGES = 3

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
        config = self._build_generate_config(data, output_gcs_uri)

        operation = client.models.generate_videos(
            model=data.model_name,
            prompt=data.prompt,
            config=config,
        )

        logger.info(
            "Veo generation started: generation_id=%s, model=%s, references=%s, output_gcs_uri=%s",
            data.generation_id,
            data.model_name,
            len(data.input_asset_paths),
            output_gcs_uri,
        )

        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
            logger.info(
                "Veo operation polling: generation_id=%s, done=%s",
                data.generation_id,
                operation.done,
            )

        operation_error = getattr(operation, "error", None)
        if operation_error is not None:
            logger.error(
                "Veo operation failed: generation_id=%s, error=%r, operation=%r",
                data.generation_id,
                operation_error,
                operation,
            )
            raise RuntimeError(f"Veo operation failed: {operation_error}")

        operation_response = getattr(operation, "response", None)
        if operation_response is None:
            operation_response = getattr(operation, "result", None)

        if operation_response is None:
            logger.error(
                "Veo operation finished without response: generation_id=%s, operation=%r",
                data.generation_id,
                operation,
            )
            raise RuntimeError("Veo operation finished without response")

        logger.info(
            "Veo operation finished: generation_id=%s, response=%r",
            data.generation_id,
            operation_response,
        )

        rai_media_filtered_count = getattr(operation_response, "rai_media_filtered_count", None)
        if rai_media_filtered_count:
            logger.warning(
                "Veo filtered media by RAI/safety: generation_id=%s, filtered_count=%s, response=%r",
                data.generation_id,
                rai_media_filtered_count,
                operation_response,
            )

        generated_videos = self._extract_generated_videos(operation_response)
        if not generated_videos:
            logger.error(
                "Veo returned no generated videos: generation_id=%s, response=%r, operation=%r",
                data.generation_id,
                operation_response,
                operation,
            )
            raise RuntimeError("Veo did not return generated videos")

        assets: list[GeneratedAsset] = []

        for index, generated_video in enumerate(generated_videos, start=1):
            video_uri = self._extract_video_uri(generated_video)

            if video_uri is None:
                logger.warning(
                    "Veo generated video has no GCS URI: generation_id=%s, generated_video=%r",
                    data.generation_id,
                    generated_video,
                )
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

    def _build_generate_config(
            self,
            data: GenerateInput,
            output_gcs_uri: str,
    ) -> types.GenerateVideosConfig:
        reference_images = self._build_reference_images(data)

        config_kwargs: dict[str, object] = {
            "number_of_videos": 1,
            "duration_seconds": 8,
            "aspect_ratio": "16:9",
            "enhance_prompt": True,
            "output_gcs_uri": output_gcs_uri,
        }

        if reference_images is not None:
            config_kwargs["reference_images"] = reference_images

        return types.GenerateVideosConfig(**config_kwargs)

    def _build_reference_images(
            self,
            data: GenerateInput,
    ) -> list[types.VideoGenerationReferenceImage] | None:
        if not data.input_asset_paths:
            return None

        if len(data.input_asset_paths) > self._MAX_REFERENCE_IMAGES:
            raise ValueError(
                f"Veo supports up to {self._MAX_REFERENCE_IMAGES} reference images"
            )

        reference_images: list[types.VideoGenerationReferenceImage] = []

        for index, input_asset_path in enumerate(data.input_asset_paths, start=1):
            private_path = self._storage.resolve_private_path(input_asset_path)
            mime_type = self._guess_image_mime_type(private_path)

            if mime_type not in self._SUPPORTED_REFERENCE_MIME_TYPES:
                raise ValueError(
                    "Unsupported Veo reference image MIME type: "
                    f"{mime_type}. Supported: image/jpeg, image/png"
                )

            reference_gcs_uri = self._upload_reference_image_to_gcs(
                data=data,
                private_path=private_path,
                mime_type=mime_type,
                index=index,
            )

            reference_images.append(
                types.VideoGenerationReferenceImage(
                    image=types.Image(
                        gcs_uri=reference_gcs_uri,
                        mime_type=mime_type,
                    ),
                    reference_type=types.VideoGenerationReferenceType.ASSET,
                )
            )

        return reference_images

    def _upload_reference_image_to_gcs(
            self,
            data: GenerateInput,
            private_path: Path,
            mime_type: str,
            index: int,
    ) -> str:
        if mime_type == "image/jpeg":
            extension = ".jpg"
        elif mime_type == "image/png":
            extension = ".png"
        else:
            raise ValueError(f"Unsupported Veo reference image MIME type: {mime_type}")

        reference_gcs_uri = (
            f"gs://{self._bucket}/"
            f"{self._prefix}/{data.generation_id}/references/reference_{index}{extension}"
        )

        self._gcs.upload_file_to_gcs_uri(
            file_path=private_path,
            gcs_uri=reference_gcs_uri,
            content_type=mime_type,
        )

        return reference_gcs_uri

    def _build_output_gcs_uri(
            self,
            data: GenerateInput,
    ) -> str:
        return f"gs://{self._bucket}/{self._prefix}/{data.generation_id}/"


    def _guess_image_mime_type(
            self,
            path: Path,
    ) -> str:
        mime_type, _ = mimetypes.guess_type(path.name)

        if mime_type is None:
            raise ValueError(f"Cannot detect MIME type for reference image: {path}")

        return mime_type

    def _extract_generated_videos(
            self,
            operation_response: object,
    ) -> list[object]:
        generated_videos = getattr(operation_response, "generated_videos", None)

        if generated_videos is None:
            return []

        if not isinstance(generated_videos, Iterable):
            return []

        return list(generated_videos)

    def _extract_video_uri(
            self,
            generated_video: object,
    ) -> str | None:
        video = getattr(generated_video, "video", None)
        video_uri = getattr(video, "uri", None)

        if not isinstance(video_uri, str):
            return None

        if not video_uri:
            return None

        return video_uri
