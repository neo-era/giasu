from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.config import settings
from app.ocr.router import router as ocr_router

app = FastAPI(title="Gia su AI - Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ocr_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
