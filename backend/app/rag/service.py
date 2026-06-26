import math

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models import TaiLieu
from app.personas import get_persona_loader


class RagResult(BaseModel):
    khop_voi_nguon: str = "khong_du_can_cu"
    diem_khac_biet: list[str] = []
    trich_dan: list[dict] = []
    do_tin_cay: float = 0.0
    can_nguoi_duyet: bool = True


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def ingest(db: Session, nguon: str, noi_dung: str, llm: LLMService | None = None) -> TaiLieu:
    svc = llm or get_llm_service()
    emb = svc.embed([noi_dung])[0]
    doc = TaiLieu(nguon=nguon, noi_dung=noi_dung, embedding=emb)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def truy_hoi(
    db: Session, truy_van: str, k: int = 3, llm: LLMService | None = None
) -> list[tuple[TaiLieu, float]]:
    svc = llm or get_llm_service()
    q = svc.embed([truy_van])[0]
    docs = list(db.scalars(select(TaiLieu)).all())
    scored = [(d, _cosine(q, d.embedding or [])) for d in docs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


def doi_chieu(
    db: Session,
    loi_giai: str,
    truy_van: str,
    k: int = 3,
    llm: LLMService | None = None,
) -> RagResult:
    svc = llm or get_llm_service()
    docs = truy_hoi(db, truy_van, k, svc)
    if not docs:
        # Không có nguồn → KHÔNG bịa; trả không đủ căn cứ + chuyển người duyệt.
        return RagResult()

    context = "\n".join(f"[{d.nguon}] {d.noi_dung}" for d, _ in docs)
    system = get_persona_loader().load("rag_doi_chieu").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=f"LỜI GIẢI:\n{loi_giai}\n\nĐOẠN TRÍCH:\n{context}"),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return RagResult()
    return RagResult(
        khop_voi_nguon=str(data.get("khop_voi_nguon", "khong_du_can_cu")),
        diem_khac_biet=list(data.get("diem_khac_biet", [])),
        trich_dan=list(data.get("trich_dan", [])),
        do_tin_cay=float(data.get("do_tin_cay", 0.0) or 0.0),
        can_nguoi_duyet=bool(data.get("can_nguoi_duyet", True)),
    )
