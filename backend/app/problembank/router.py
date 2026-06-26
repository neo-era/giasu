from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.db.session import get_db
from app.models import DeBai, NguoiDung
from app.models.enums import DoKho, VaiTro
from app.problembank.schemas import GeneratedProblemOut, GenerateIn, ProblemStudentOut
from app.problembank.service import ProblemBankService
from app.verify import can_nguoi_duyet

router = APIRouter(prefix="/problems", tags=["problems"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/generate", response_model=list[GeneratedProblemOut], status_code=201)
def generate(
    body: GenerateIn,
    db: DbDep,
    _: Annotated[NguoiDung, Depends(require_roles(VaiTro.bien_tap, VaiTro.quan_tri))],
) -> list[GeneratedProblemOut]:
    ket_qua = ProblemBankService(db).generate(body)
    return [
        GeneratedProblemOut(
            id=de.id,
            de_latex=de.de_latex,
            chuong=de.chuong,
            do_kho=de.do_kho,
            dap_so=lg.dap_so,
            kiem_trang_thai=vr.trang_thai.value,
            can_nguoi_duyet=can_nguoi_duyet(vr),
        )
        for de, lg, vr in ket_qua
    ]


@router.get("", response_model=list[ProblemStudentOut])
def list_problems(
    db: DbDep,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
    lop: int | None = None,
    chuong: str | None = None,
    do_kho: DoKho | None = None,
) -> list[DeBai]:
    stmt = select(DeBai)
    if lop is not None:
        stmt = stmt.where(DeBai.lop == lop)
    if chuong is not None:
        stmt = stmt.where(DeBai.chuong == chuong)
    if do_kho is not None:
        stmt = stmt.where(DeBai.do_kho == do_kho)
    return list(db.scalars(stmt.order_by(DeBai.created_at.desc())).all())
