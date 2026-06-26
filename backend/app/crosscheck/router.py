from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.crosscheck.service import (
    ComparisonResult,
    chay_cross_check,
    duyet,
    hang_doi_cho_duyet,
)
from app.db.session import get_db
from app.models import NguoiDung
from app.models.enums import VaiTro

router = APIRouter(tags=["crosscheck"])

DbDep = Annotated[Session, Depends(get_db)]
DuyetDep = Annotated[NguoiDung, Depends(require_roles(VaiTro.hlv, VaiTro.quan_tri))]


class CrossCheckIn(BaseModel):
    cau_hoi: str


class CrossCheckOut(BaseModel):
    comparison: ComparisonResult
    review_id: str | None


class ReviewItemOut(BaseModel):
    id: str
    loai: str
    noi_dung: str
    trang_thai: str


class ResolveIn(BaseModel):
    ket_luan: str


@router.post("/crosscheck", response_model=CrossCheckOut)
def crosscheck(
    body: CrossCheckIn,
    db: DbDep,
    _: Annotated[NguoiDung, Depends(get_current_active_user)],
) -> CrossCheckOut:
    cmp, review_id = chay_cross_check(db, body.cau_hoi)
    return CrossCheckOut(comparison=cmp, review_id=review_id)


@router.get("/review/queue", response_model=list[ReviewItemOut])
def queue(db: DbDep, _: DuyetDep) -> list[ReviewItemOut]:
    return [
        ReviewItemOut(id=i.id, loai=i.loai, noi_dung=i.noi_dung, trang_thai=i.trang_thai.value)
        for i in hang_doi_cho_duyet(db)
    ]


@router.post("/review/{item_id}/resolve", response_model=ReviewItemOut)
def resolve(item_id: str, body: ResolveIn, db: DbDep, user: DuyetDep) -> ReviewItemOut:
    item = duyet(db, user, item_id, body.ket_luan)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy mục duyệt")
    return ReviewItemOut(
        id=item.id, loai=item.loai, noi_dung=item.noi_dung, trang_thai=item.trang_thai.value
    )
