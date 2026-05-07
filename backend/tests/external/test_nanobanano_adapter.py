from uuid import uuid4

import pytest

from app.ai.adapters.nanobanano import NanoBananoAdapter
from app.ai.base import GenerateImageInput


pytestmark = [pytest.mark.asyncio, pytest.mark.external]


async def test_nanobanano_text_to_image_smoke() -> None:
    adapter = NanoBananoAdapter()

    result = await adapter.generate_image(
        GenerateImageInput(
            generation_id=uuid4(),
            prompt="A cute banana astronaut, 3d render, clean background",
            input_image_paths=[],
            model_name="gemini-2.5-flash-image",
        )
    )

    assert result.output_image_paths