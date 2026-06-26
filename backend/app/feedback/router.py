from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.db.session import get_db
from app.feedback.schemas import FeedbackCreate, FeedbackOut
from app.feedback.service import liet_ke, tao_phan_anh, to_out
from app.models import NguoiDung
from app.models.enums import ChuDePhanAnh, TrangThaiPhanAnh

router = APIRouter(prefix="/feedback", tags=["feedback"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


@router.post("", response_model=FeedbackOut, status_code=201)
def create_feedback(body: FeedbackCreate, db: DbDep, user: UserDep) -> FeedbackOut:
    pa = tao_phan_anh(db, user, body)
    db.commit()
    db.refresh(pa)
    return to_out(pa)


@router.get("", response_model=list[FeedbackOut])
def list_feedback(
    db: DbDep,
    _: UserDep,
    chu_de: ChuDePhanAnh | None = None,
    trang_thai: TrangThaiPhanAnh | None = None,
    sap_xep: str = "moi_nhat",
) -> list[FeedbackOut]:
    items = liet_ke(db, chu_de=chu_de, trang_thai=trang_thai, sap_xep=sap_xep)
    return [to_out(p) for p in items]
