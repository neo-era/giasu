from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.models import NguoiDung
from app.translate.service import DichResult, dich

router = APIRouter(prefix="/dich", tags=["dich"])


class DichIn(BaseModel):
    noi_dung: str


@router.post("", response_model=DichResult)
def dich_endpoint(
    body: DichIn,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> DichResult:
    return dich(body.noi_dung)
