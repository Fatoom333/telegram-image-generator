from fastapi import FastAPI

app = FastAPI(title="Telegram Image Generator API")

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}