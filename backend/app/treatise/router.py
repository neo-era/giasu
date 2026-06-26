from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.deps import require_roles
from app.models import NguoiDung
from app.models.enums import VaiTro
from app.treatise.service import ChuaDuyetError, ChuyenLuan, bien_tap

router = APIRouter(prefix="/chuyen-luan", tags=["chuyen-luan"])


class ChuyenLuanIn(BaseModel):
    noi_dung: str
    da_duyet: bool = False


@router.post("", response_model=ChuyenLuan)
def xuat(
    body: ChuyenLuanIn,
    _: Annotated[NguoiDung, Depends(require_roles(VaiTro.hlv, VaiTro.quan_tri, VaiTro.bien_tap))],
) -> ChuyenLuan:
    try:
        return bien_tap(body.noi_dung, body.da_duyet)
    except ChuaDuyetError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
