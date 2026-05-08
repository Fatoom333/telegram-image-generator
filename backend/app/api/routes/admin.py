from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db_session
from app.db.models.generation import Generation
from app.db.models.purchase import Purchase
from app.db.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/stats")
async def get_admin_stats(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    users_count = await session.scalar(select(func.count()).select_from(User))
    generations_count = await session.scalar(select(func.count()).select_from(Generation))
    purchases_count = await session.scalar(select(func.count()).select_from(Purchase))

    return {
        "users_count": users_count or 0,
        "generations_count": generations_count or 0,
        "purchases_count": purchases_count or 0,
    }