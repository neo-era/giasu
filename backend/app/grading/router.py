from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.grading.service import GradeResult, cham
from app.models import NguoiDung

router = APIRouter(prefix="/grade", tags=["grading"])


class GradeIn(BaseModel):
    bai_lam: str
    loi_giai_mau: str
    barem: str
    diem_toi_da: float | None = None


@router.post("", response_model=GradeResult)
def grade(
    body: GradeIn,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> GradeResult:
    return cham(body.bai_lam, body.loi_giai_mau, body.barem, body.diem_toi_da)
