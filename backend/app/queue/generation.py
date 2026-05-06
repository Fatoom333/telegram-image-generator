from uuid import UUID

from arq import create_pool

from app.queue.redis import get_arq_redis_settings


GENERATE_IMAGE_JOB_NAME = "generate_image"


async def enqueue_generation_task(
    generation_id: UUID,
) -> None:
    redis = await create_pool(get_arq_redis_settings())

    try:
        await redis.enqueue_job(
            GENERATE_IMAGE_JOB_NAME,
            str(generation_id),
        )
    finally:
        await redis.close()
