from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import ai_models, balance, credits, generations, purchases, users
from app.core.config import BACKEND_DIR, settings


app = FastAPI(title="Telegram Image Generator API")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


storage_path = BACKEND_DIR / settings.storage_dir
storage_path.mkdir(parents=True, exist_ok=True)

app.mount(
    settings.public_storage_url,
    StaticFiles(directory=storage_path),
    name="media",
)


app.include_router(users.router, prefix="/api")
app.include_router(balance.router, prefix="/api")
app.include_router(credits.router, prefix="/api")
app.include_router(ai_models.router, prefix="/api")
app.include_router(generations.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")