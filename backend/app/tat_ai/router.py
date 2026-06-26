from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.db.session import get_db
from app.metrics.service import ghi_do, ty_le_tu_giai
from app.models import NguoiDung
from app.models.enums import GiaiDoanDo, NhomThuNghiem
from app.tat_ai.service import bang_tu_giai, hieu_chinh_do_kho, sinh_de

router = APIRouter(prefix="/tat-ai", tags=["tat-ai"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


class DeIn(BaseModel):
    khai_niem: list[str] = []


class KetQuaIn(BaseModel):
    diem: float
    thang_diem: float = 10.0


@router.post("/de")
def tao_de(body: DeIn, _: UserDep) -> dict:
    return sinh_de(body.khai_niem)


@router.post("/ket-qua", status_code=201)
def ghi_ket_qua(body: KetQuaIn, db: DbDep, user: UserDep) -> dict:
    # Đo khi TẮT AI → ghi như điểm post (NFR-50/51)
    ghi_do(
        db,
        user.id,
        GiaiDoanDo.post,
        body.diem,
        tat_ai=True,
        nhom=NhomThuNghiem.app,
    )
    db.commit()
    return {"hieu_chinh_do_kho": hieu_chinh_do_kho(body.diem, body.thang_diem)}


@router.get("/bang")
def bang(db: DbDep, user: UserDep) -> dict:
    return {
        "ty_le_tu_giai": bang_tu_giai(db, user.id),
        "trung_binh": ty_le_tu_giai(db),
    }
