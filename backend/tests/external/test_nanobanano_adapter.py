import os

import pytest

from app.ai.adapters.nanobanano import NanoBananoAdapter
from app.ai.base import GenerateImageInput


@pytest.mark.external
@pytest.mark.skipif(
    os.getenv("RUN_EXTERNAL_TESTS") != "true",
    reason="External tests are disabled",
)
@pytest.mark.skipif(
    not os.getenv("NANOBANANO_API_KEY"),
    reason="NANOBANANO_API_KEY is not configured",
)
async def test_nanobanano_adapter_real_request() -> None:
    adapter = NanoBananoAdapter()

    result = await adapter.generate_image(
        GenerateImageInput(
            prompt="cute corgi wizard, fantasy style",
            input_image_paths=[],
            model_name="nanobanano-v1",
        )
    )

    assert len(result.output_image_paths) > 0