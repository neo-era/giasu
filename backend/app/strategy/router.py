from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import get_current_active_user
from app.models import NguoiDung
from app.strategy.service import StrategyTree, sinh_cay

router = APIRouter(prefix="/strategy", tags=["strategy"])


class TreeIn(BaseModel):
    de_latex: str


@router.post("/tree", response_model=StrategyTree)
def tree(
    body: TreeIn,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> StrategyTree:
    return sinh_cay(body.de_latex)
