from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.db.session import get_db
from app.models import NguoiDung
from app.models.enums import VaiTro
from app.rag.service import RagResult, doi_chieu, ingest

router = APIRouter(prefix="/rag", tags=["rag"])

DbDep = Annotated[Session, Depends(get_db)]


class IngestIn(BaseModel):
    nguon: str
    noi_dung: str


class DoiChieuIn(BaseModel):
    loi_giai: str
    truy_van: str


@router.post("/ingest", status_code=201)
def ingest_doc(
    body: IngestIn,
    db: DbDep,
    _: Annotated[NguoiDung, Depends(require_roles(VaiTro.bien_tap, VaiTro.quan_tri))],
) -> dict[str, str]:
    doc = ingest(db, body.nguon, body.noi_dung)
    return {"id": doc.id}


@router.post("/doi-chieu", response_model=RagResult)
def doi_chieu_endpoint(
    body: DoiChieuIn,
    db: DbDep,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> RagResult:
    return doi_chieu(db, body.loi_giai, body.truy_van)
