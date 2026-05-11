from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.credits import BalanceResponse

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("", response_model=BalanceResponse)
async def get_balance(
        current_user: User = Depends(get_current_user),
) -> BalanceResponse:
    return BalanceResponse(credits=current_user.credits)
