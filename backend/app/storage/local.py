from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import BACKEND_DIR, settings


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
            extension = self._get_extension(file.filename)

            file_name = f"input_{index}{extension}"
            file_path = generation_dir / file_name

            content = await file.read()
            file_path.write_bytes(content)

            relative_path = Path("generations") / str(generation_id) / file_name
            saved_paths.append(str(relative_path).replace("\\", "/"))

        return saved_paths

    def to_public_url(
        self,
        relative_path: str,
    ) -> str:
        return f"{settings.public_storage_url}/{relative_path}"

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