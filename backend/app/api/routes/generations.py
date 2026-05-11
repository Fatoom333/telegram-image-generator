from pathlib import Path
from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.model_catalog import ModelCatalog
from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.db.models.user import User
from app.queue.generation import enqueue_generation_task
from app.repositories.generation_images import GenerationImageRepository
from app.schemas.generations import GenerationAssetResponse, GenerationResponse
from app.services.exceptions import (
    AIModelNotFoundError,
    EmptyPromptError,
    GenerationNotFoundError,
    NotEnoughCreditsError,
    TooManyInputImagesError,
    UserBannedError,
)
from app.services.generations import GenerationService
from app.storage.local import LocalFileStorage

router = APIRouter(prefix="/generations", tags=["generations"])

VEO_REFERENCE_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
}


@router.post("", response_model=GenerationResponse)
async def create_generation(
        prompt: Annotated[str, Form()],
        provider: Annotated[str | None, Form()] = None,
        model_name: Annotated[str | None, Form()] = None,
        images: Annotated[list[UploadFile] | None, File()] = None,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
) -> GenerationResponse:
    images = images or []
    storage = LocalFileStorage()
    model_catalog = ModelCatalog()

    try:
        async with session.begin():
            generation_service = GenerationService(session)

            generation = await generation_service.create_generation(
                telegram_id=current_user.telegram_id,
                prompt=prompt,
                provider=provider,
                model_name=model_name,
                input_assets_cnt=len(images),
            )

            if generation.provider is None or generation.model_name is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Generation model was not selected",
                )

            selected_model = model_catalog.get_model(
                provider=generation.provider,
                model_name=generation.model_name,
            )

            input_asset_paths = await storage.save_generation_reference_assets(
                generation_id=generation.id,
                files=images,
                output_asset_type=selected_model.output_asset_type,
            )

            await generation_service.add_input_assets(
                generation_id=generation.id,
                input_asset_paths=input_asset_paths,
            )

            generation = await generation_service.get_generation_for_user(
                generation_id=generation.id,
                telegram_id=current_user.telegram_id,
            )
            generation_id = generation.id

        await enqueue_generation_task(generation_id)

        return _generation_to_response(generation)

    except EmptyPromptError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is empty",
        )
    except TooManyInputImagesError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many input images",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    except AIModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI model was not found",
        )
    except NotEnoughCreditsError:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough credits",
        )
    except UserBannedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is banned",
        )


@router.get("", response_model=list[GenerationResponse])
async def list_generations(
        limit: int = 20,
        offset: int = 0,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
) -> list[GenerationResponse]:
    generation_service = GenerationService(session)
    generations = await generation_service.list_user_generations(
        telegram_id=current_user.telegram_id,
        limit=limit,
        offset=offset,
    )

    return [
        _generation_to_response(generation)
        for generation in generations
    ]


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(
        generation_id: UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
) -> GenerationResponse:
    generation_service = GenerationService(session)

    try:
        generation = await generation_service.get_generation_for_user(
            generation_id=generation_id,
            telegram_id=current_user.telegram_id,
        )
    except GenerationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    return _generation_to_response(generation)


@router.get("/{generation_id}/assets/{asset_id}")
async def get_generation_asset(
        generation_id: UUID,
        asset_id: UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
) -> FileResponse:
    return await _get_generation_asset_file_response(
        generation_id=generation_id,
        asset_id=asset_id,
        current_user=current_user,
        session=session,
    )


@router.get("/{generation_id}/images/{image_id}")
async def get_generation_image(
        generation_id: UUID,
        image_id: UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
) -> FileResponse:
    return await _get_generation_asset_file_response(
        generation_id=generation_id,
        asset_id=image_id,
        current_user=current_user,
        session=session,
    )


async def _get_generation_asset_file_response(
        generation_id: UUID,
        asset_id: UUID,
        current_user: User,
        session: AsyncSession,
) -> FileResponse:
    storage = LocalFileStorage()
    generation_service = GenerationService(session)
    generation_image_repository = GenerationImageRepository(session)

    try:
        await generation_service.get_generation_for_user(
            generation_id=generation_id,
            telegram_id=current_user.telegram_id,
        )
    except GenerationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    asset = await generation_image_repository.get_by_id_for_generation(
        generation_id=generation_id,
        asset_id=asset_id,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    try:
        file_path = storage.resolve_private_path(asset.file_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset path",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset file not found",
        )

    return FileResponse(
        path=file_path,
        media_type=asset.mime_type or _guess_media_type(file_path),
        filename=file_path.name,
    )


def _generation_to_response(
        generation: Any,
) -> GenerationResponse:
    response = GenerationResponse.model_validate(generation)

    assets = [
        _asset_to_response(
            generation_id=generation.id,
            asset=asset,
        )
        for asset in generation.images
    ]

    response.assets = assets
    response.images = assets

    return response


def _asset_to_response(
        generation_id: UUID,
        asset: Any,
) -> GenerationAssetResponse:
    response = GenerationAssetResponse.model_validate(asset)
    response.file_url = f"/api/generations/{generation_id}/assets/{asset.id}"

    return response


def _guess_media_type(
        file_path: Path,
) -> str:
    suffix = file_path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"

    if suffix == ".png":
        return "image/png"

    if suffix == ".webp":
        return "image/webp"

    if suffix == ".mp4":
        return "video/mp4"

    return "application/octet-stream"
