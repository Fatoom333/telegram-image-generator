from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import BACKEND_DIR, settings


MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

OUTPUT_IMAGE_MIME_TYPE_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class LocalFileStorage:
    def __init__(self) -> None:
        self._storage_root = BACKEND_DIR / settings.storage_dir

    async def save_generation_input_images(
        self,
        generation_id: UUID,
        files: list[UploadFile],
    ) -> list[str]:
        generation_dir = self._storage_root / "generations" / str(generation_id)
        generation_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[str] = []

        for index, file in enumerate(files, start=1):
            if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValueError("Unsupported image type")

            extension = self._get_extension(file.filename)
            file_name = f"input_{index}{extension}"
            file_path = generation_dir / file_name

            await self._save_file_with_size_limit(
                file=file,
                file_path=file_path,
            )

            relative_path = Path("generations") / str(generation_id) / file_name
            saved_paths.append(str(relative_path).replace("\\", "/"))

        return saved_paths

    def save_generation_output_image_bytes(
        self,
        generation_id: UUID,
        image_bytes: bytes,
        mime_type: str,
        index: int,
    ) -> str:
        extension = OUTPUT_IMAGE_MIME_TYPE_TO_EXTENSION.get(mime_type)
        if extension is None:
            raise ValueError(f"Unsupported output image type: {mime_type}")

        generation_dir = self._storage_root / "generations" / str(generation_id)
        generation_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"output_{index}{extension}"
        file_path = generation_dir / file_name
        file_path.write_bytes(image_bytes)

        relative_path = Path("generations") / str(generation_id) / file_name
        return str(relative_path).replace("\\", "/")

    def resolve_private_path(self, relative_path: str) -> Path:
        storage_root = self._storage_root.resolve()
        file_path = (storage_root / relative_path).resolve()

        if storage_root not in file_path.parents and file_path != storage_root:
            raise ValueError("Path traversal detected")

        return file_path

    async def _save_file_with_size_limit(
        self,
        file: UploadFile,
        file_path: Path,
    ) -> None:
        total_size = 0

        with file_path.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > MAX_IMAGE_SIZE_BYTES:
                    output_file.close()
                    file_path.unlink(missing_ok=True)
                    raise ValueError("Image too large")

                output_file.write(chunk)

        await file.seek(0)

    @staticmethod
    def _get_extension(filename: str | None) -> str:
        if not filename:
            return ".bin"

        suffix = Path(filename).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            return suffix

        return ".bin"