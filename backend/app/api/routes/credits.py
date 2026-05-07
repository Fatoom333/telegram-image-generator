from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.db.models.user import User
from app.schemas.credits import CreditTransactionResponse
from app.services.credits import CreditService


router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/transactions", response_model=list[CreditTransactionResponse])
async def list_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list:
    credit_service = CreditService(session)

    return await credit_service.list_transactions(
        telegram_id=current_user.telegram_id,
        limit=limit,
        offset=offset,
    )
