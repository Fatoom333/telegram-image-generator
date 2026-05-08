from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str | None
    credits: int
    is_banned: bool
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)