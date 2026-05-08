from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models.user import User
from app.schemas.users import UserResponse


router = APIRouter(prefix="/me", tags=["me"])


def build_user_response(user: User) -> UserResponse:
    response = UserResponse.model_validate(user)
    response.is_admin = user.telegram_id in settings.admin_telegram_id_set
    return response


@router.get("", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return build_user_response(current_user)