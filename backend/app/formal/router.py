from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.formal.service import FormalResult, hinh_thuc_hoa
from app.models import NguoiDung

router = APIRouter(prefix="/formal", tags=["formal"])


class HinhThucHoaIn(BaseModel):
    menh_de: str


@router.post("/hinh-thuc-hoa", response_model=FormalResult)
def hinh_thuc_hoa_endpoint(
    body: HinhThucHoaIn,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> FormalResult:
    return hinh_thuc_hoa(body.menh_de)
