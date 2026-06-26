from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.db.session import get_db
from app.metrics.service import dashboard, ghi_do
from app.models import NguoiDung
from app.models.enums import GiaiDoanDo, NhomThuNghiem, VaiTro

router = APIRouter(prefix="/metrics", tags=["metrics"])

DbDep = Annotated[Session, Depends(get_db)]


class DoIn(BaseModel):
    giai_doan: GiaiDoanDo
    diem: float
    tat_ai: bool = True
    nhom: NhomThuNghiem = NhomThuNghiem.app


@router.post("/learning", status_code=201)
def record_learning(
    body: DoIn,
    db: DbDep,
    user: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> dict[str, str]:
    rec = ghi_do(db, user.id, body.giai_doan, body.diem, tat_ai=body.tat_ai, nhom=body.nhom)
    db.commit()
    return {"id": rec.id}


@router.get("/dashboard")
def get_dashboard(
    db: DbDep,
    _: Annotated[NguoiDung, Depends(require_roles(VaiTro.quan_tri, VaiTro.bien_tap))],
) -> dict:
    return dashboard(db)
