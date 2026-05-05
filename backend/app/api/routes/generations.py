from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.db.models.user import User
from app.schemas.generations import GenerationResponse
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

    try:
        async with session.begin():
            generation_service = GenerationService(session)

            generation = await generation_service.create_generation(
                telegram_id=current_user.telegram_id,
                prompt=prompt,
                provider=provider,
                model_name=model_name,
                input_images_cnt=len(images),
            )

            input_image_paths = await storage.save_generation_input_images(
                generation_id=generation.id,
                files=images,
            )

            await generation_service.add_input_images(
                generation_id=generation.id,
                input_image_paths=input_image_paths,
            )

            generation = await generation_service.get_generation_for_user(
                generation_id=generation.id,
                telegram_id=current_user.telegram_id,
            )

        return _generation_to_response(generation, storage)

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
    storage = LocalFileStorage()
    generation_service = GenerationService(session)

    generations = await generation_service.list_user_generations(
        telegram_id=current_user.telegram_id,
        limit=limit,
        offset=offset,
    )

    return [
        _generation_to_response(generation, storage)
        for generation in generations
    ]


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> GenerationResponse:
    storage = LocalFileStorage()
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

    return _generation_to_response(generation, storage)


def _generation_to_response(
    generation: Any,
    storage: LocalFileStorage,
) -> GenerationResponse:
    response = GenerationResponse.model_validate(generation)

    for image in response.images:
        image.file_url = storage.to_public_url(image.file_path)

    return response
