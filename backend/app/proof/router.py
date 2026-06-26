from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.models import NguoiDung
from app.proof.service import CritiqueResult, critique

router = APIRouter(prefix="/proof", tags=["proof"])


class CritiqueIn(BaseModel):
    chung_minh: str


@router.post("/critique", response_model=CritiqueResult)
def critique_proof(
    body: CritiqueIn,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> CritiqueResult:
    return critique(body.chung_minh)
