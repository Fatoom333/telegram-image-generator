from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import BACKEND_DIR, settings


MAX_REFERENCE_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_REFERENCE_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ASSET_MIME_TYPE_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
}


class LocalFileStorage:
    def __init__(self) -> None:
        self._storage_root = BACKEND_DIR / settings.storage_dir

    async def save_generation_reference_assets(
        self,
        generation_id: UUID,
        files: list[UploadFile],
        output_asset_type: str,
    ) -> list[str]:
        media_folder = self._get_media_folder(output_asset_type)
        generation_dir = self._get_generation_media_dir(
            media_folder=media_folder,
            generation_id=generation_id,
        )
        generation_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[str] = []

        for index, file in enumerate(files, start=1):
            if file.content_type not in ALLOWED_REFERENCE_IMAGE_MIME_TYPES:
                raise ValueError("Unsupported reference image type")

            extension = self._get_reference_image_extension(file.filename)
            file_name = f"reference_{index}{extension}"
            file_path = generation_dir / file_name

            await self._save_file_with_size_limit(
                file=file,
                file_path=file_path,
                max_size_bytes=MAX_REFERENCE_IMAGE_SIZE_BYTES,
            )

            saved_paths.append(
                self._build_relative_media_path(
                    media_folder=media_folder,
                    generation_id=generation_id,
                    file_name=file_name,
                )
            )

        return saved_paths

    def save_generation_output_asset_bytes(
        self,
        generation_id: UUID,
        asset_bytes: bytes,
        asset_type: str,
        mime_type: str,
        index: int,
    ) -> str:
        extension = ASSET_MIME_TYPE_TO_EXTENSION.get(mime_type)
        if extension is None:
            raise ValueError(f"Unsupported output asset type: {mime_type}")

        media_folder = self._get_media_folder(asset_type)
        generation_dir = self._get_generation_media_dir(
            media_folder=media_folder,
            generation_id=generation_id,
        )
        generation_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"output_{index}{extension}"
        file_path = generation_dir / file_name
        file_path.write_bytes(asset_bytes)

        return self._build_relative_media_path(
            media_folder=media_folder,
            generation_id=generation_id,
            file_name=file_name,
        )

    def resolve_private_path(
        self,
        relative_path: str,
    ) -> Path:
        storage_root = self._storage_root.resolve()
        file_path = (storage_root / relative_path).resolve()

        if storage_root not in file_path.parents and file_path != storage_root:
            raise ValueError("Path traversal detected")

        return file_path

    async def _save_file_with_size_limit(
        self,
        file: UploadFile,
        file_path: Path,
        max_size_bytes: int,
    ) -> None:
        total_size = 0

        with file_path.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > max_size_bytes:
                    output_file.close()
                    file_path.unlink(missing_ok=True)
                    raise ValueError("File is too large")

                output_file.write(chunk)

        await file.seek(0)

    def _get_generation_media_dir(
        self,
        media_folder: str,
        generation_id: UUID,
    ) -> Path:
        return self._storage_root / "generated" / media_folder / str(generation_id)

    @staticmethod
    def _build_relative_media_path(
        media_folder: str,
        generation_id: UUID,
        file_name: str,
    ) -> str:
        relative_path = Path("generated") / media_folder / str(generation_id) / file_name
        return str(relative_path).replace("\\", "/")

    @staticmethod
    def _get_media_folder(
        asset_type: str,
    ) -> str:
        if asset_type == "image":
            return "image"

        if asset_type == "video":
            return "video"

        raise ValueError(f"Unsupported asset type: {asset_type}")

    @staticmethod
    def _get_reference_image_extension(
        filename: str | None,
    ) -> str:
        if not filename:
            return ".bin"

        suffix = Path(filename).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            return suffix

        return ".bin"