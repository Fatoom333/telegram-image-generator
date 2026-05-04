from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_session import UserSession
from app.repositories.user_sessions import UserSessionRepository
from app.repositories.users import UserRepository
from app.services.exceptions import TooManyInputImagesError, UserNotFoundError


class UserSessionState:
    IDLE = "idle"
    COLLECTING_REFERENCES = "collecting_references"
    WAITING_PROMPT_AFTER_REFERENCES = "waiting_prompt_after_references"
    GENERATING = "generating"


class UserSessionService:
    MAX_REFERENCE_IMAGES = 4

    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._sessions = UserSessionRepository(session)

    async def get_or_create_session(
        self,
        telegram_id: int,
    ) -> UserSession:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        return await self._sessions.get_or_create(telegram_id=telegram_id)

    async def set_state(
        self,
        telegram_id: int,
        state: str,
        payload: dict | None = None,
    ) -> UserSession:
        user_session = await self.get_or_create_session(telegram_id)

        return await self._sessions.update(
            session=user_session,
            state=state,
            payload=payload,
        )

    async def reset(
        self,
        telegram_id: int,
    ) -> UserSession:
        user_session = await self.get_or_create_session(telegram_id)

        return await self._sessions.reset(session=user_session)

    async def start_collecting_references(
        self,
        telegram_id: int,
    ) -> UserSession:
        return await self.set_state(
            telegram_id=telegram_id,
            state=UserSessionState.COLLECTING_REFERENCES,
            payload={"references": []},
        )

    async def add_reference_image(
        self,
        telegram_id: int,
        file_path: str,
        telegram_file_id: str | None = None,
    ) -> UserSession:
        user_session = await self.get_or_create_session(telegram_id)

        payload = dict(user_session.payload)
        references = list(payload.get("references", []))

        if len(references) >= self.MAX_REFERENCE_IMAGES:
            raise TooManyInputImagesError

        references.append(
            {
                "file_path": file_path,
                "telegram_file_id": telegram_file_id,
            }
        )

        payload["references"] = references

        return await self._sessions.update(
            session=user_session,
            state=UserSessionState.WAITING_PROMPT_AFTER_REFERENCES,
            payload=payload,
        )

    async def get_reference_paths(
        self,
        telegram_id: int,
    ) -> list[str]:
        user_session = await self.get_or_create_session(telegram_id)

        references = user_session.payload.get("references", [])

        return [
            reference["file_path"]
            for reference in references
            if "file_path" in reference
        ]

    async def mark_generating(
        self,
        telegram_id: int,
    ) -> UserSession:
        user_session = await self.get_or_create_session(telegram_id)

        payload = dict(user_session.payload)

        return await self._sessions.update(
            session=user_session,
            state=UserSessionState.GENERATING,
            payload=payload,
        )
