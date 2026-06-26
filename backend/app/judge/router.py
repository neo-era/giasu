from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.judge.service import JudgeResult, TestResult, cham, phan_tich, sandbox_san_sang
from app.models import NguoiDung

router = APIRouter(prefix="/judge", tags=["judge"])

UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


class ChamIn(BaseModel):
    test_results: list[TestResult]
    time_limit_ms: int = 1000
    mem_limit_kb: int = 262144


class RunIn(BaseModel):
    ngon_ngu: str
    ma_nguon: str


class PhanTichIn(BaseModel):
    de: str
    ma_nguon: str
    ket_qua_judge: str


@router.post("/cham", response_model=JudgeResult)
def cham_endpoint(body: ChamIn, _: UserDep) -> JudgeResult:
    return cham(body.test_results, body.time_limit_ms, body.mem_limit_kb)


@router.post("/run")
def run(body: RunIn, _: UserDep) -> dict:
    # Cổng an toàn: sandbox chưa qua kiểm thử bảo mật → KHÔNG thực thi mã (FR-E07).
    if not sandbox_san_sang():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Sandbox chưa được bật (chờ qua kiểm thử bảo mật)",
        )
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Bộ thực thi sandbox sẽ tích hợp sau")


@router.post("/phan-tich")
def phan_tich_endpoint(body: PhanTichIn, _: UserDep) -> dict:
    return phan_tich(body.de, body.ma_nguon, body.ket_qua_judge)
