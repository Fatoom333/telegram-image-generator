from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from aiogram import Bot
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, status

from app.api.routes import admin, ai_models, balance, credits, generations, purchases, users
from app.bot.dispatcher import create_dispatcher
from app.core.config import BACKEND_DIR, settings

bot = Bot(token=settings.telegram_bot_token)
dispatcher = create_dispatcher()


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    webhook_url = f"{settings.webhook_base_url}{settings.telegram_webhook_path}"

    await bot.set_webhook(
        webhook_url,
        secret_token=settings.telegram_webhook_secret,
        drop_pending_updates=True,
    )

    yield

    await bot.delete_webhook(drop_pending_updates=False)

    if bot.session is not None:
        await bot.session.close()


app = FastAPI(
    title="Telegram Image Generator API",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram webhook secret",
        )

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot, update)

    return {"ok": True}


storage_path = BACKEND_DIR / settings.storage_dir
storage_path.mkdir(parents=True, exist_ok=True)

app.include_router(users.router, prefix="/api")
app.include_router(balance.router, prefix="/api")
app.include_router(credits.router, prefix="/api")
app.include_router(ai_models.router, prefix="/api")
app.include_router(generations.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")
app.include_router(admin.router, prefix="/api")