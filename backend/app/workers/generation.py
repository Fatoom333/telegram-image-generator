from uuid import UUID

from app.core.database import async_session_factory
from app.queue.redis import get_arq_redis_settings
from app.services.ai_execution import AIExecutionService


async def generate_image(
    ctx,
    generation_id: str,
) -> None:
    generation_uuid = UUID(generation_id)

    async with async_session_factory() as session:
        async with session.begin():
            ai_execution_service = AIExecutionService(session)
            await ai_execution_service.execute_generation(generation_uuid)


class WorkerSettings:
    redis_settings = get_arq_redis_settings()
    functions = [generate_image]
    max_jobs = 5
    job_timeout = 900
    retry_jobs = False