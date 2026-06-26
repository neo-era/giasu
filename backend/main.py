from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.billing.router import router as billing_router
from app.chat.router import router as chat_router
from app.config import settings
from app.crosscheck.router import router as crosscheck_router
from app.diagnostic.router import router as diagnostic_router
from app.feedback.router import router as feedback_router
from app.grading.router import router as grading_router
from app.metrics.router import router as metrics_router
from app.ocr.router import router as ocr_router
from app.problembank.router import router as problembank_router
from app.proof.router import router as proof_router
from app.rag.router import router as rag_router
from app.spaced.router import router as spaced_router
from app.strategy.router import router as strategy_router
from app.tat_ai.router import router as tat_ai_router

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
app.include_router(diagnostic_router)
app.include_router(problembank_router)
app.include_router(billing_router)
app.include_router(feedback_router)
app.include_router(metrics_router)
app.include_router(admin_router)
app.include_router(strategy_router)
app.include_router(proof_router)
app.include_router(crosscheck_router)
app.include_router(rag_router)
app.include_router(grading_router)
app.include_router(spaced_router)
app.include_router(tat_ai_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
