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

    def resolve_private_path(self, relative_path: str) -> Path:
        storage_root = self._storage_root.resolve()
        file_path = (storage_root / relative_path).resolve()

        if storage_root not in file_path.parents and file_path != storage_root:
            raise ValueError("Invalid file path")

        return file_path

    def _get_extension(
        self,
        filename: str | None,
    ) -> str:
        if filename is None:
            return ".bin"

        suffix = Path(filename).suffix.lower()

        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            return suffix

        return ".bin"

    async def _save_file_with_size_limit(
            self,
            file: UploadFile,
            file_path: Path,
    ) -> None:
        bytes_written = 0
        chunk_size = 1024 * 1024

        try:
            with file_path.open("wb") as output_file:
                while chunk := await file.read(chunk_size):
                    bytes_written += len(chunk)

                    if bytes_written > MAX_IMAGE_SIZE_BYTES:
                        raise ValueError("Image is too large")

                    output_file.write(chunk)

        except Exception:
            file_path.unlink(missing_ok=True)
            raise