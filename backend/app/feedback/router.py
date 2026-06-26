from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.db.session import get_db
from app.feedback.schemas import (
    CommentOut,
    FeedbackCreate,
    FeedbackOut,
    ReplyIn,
    StatusIn,
)
from app.feedback.service import (
    VAI_TRO_DOI_NGU,
    doi_trang_thai,
    dong_tinh,
    giai_quyet_loi,
    liet_ke,
    liet_ke_binh_luan,
    tao_phan_anh,
    them_binh_luan,
    thong_bao_cua,
    to_out,
    tra_loi_chinh_thuc,
)
from app.models import NguoiDung, PhanAnh
from app.models.enums import ChuDePhanAnh, TrangThaiPhanAnh

router = APIRouter(prefix="/feedback", tags=["feedback"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


@router.post("", response_model=FeedbackOut, status_code=201)
def create_feedback(body: FeedbackCreate, db: DbDep, user: UserDep) -> FeedbackOut:
    pa = tao_phan_anh(db, user, body)
    db.commit()
    db.refresh(pa)
    return to_out(pa)


@router.get("", response_model=list[FeedbackOut])
def list_feedback(
    db: DbDep,
    _: UserDep,
    chu_de: ChuDePhanAnh | None = None,
    trang_thai: TrangThaiPhanAnh | None = None,
    sap_xep: str = "moi_nhat",
) -> list[FeedbackOut]:
    items = liet_ke(db, chu_de=chu_de, trang_thai=trang_thai, sap_xep=sap_xep)
    return [to_out(p) for p in items]


TeamDep = Annotated[NguoiDung, Depends(require_roles(*VAI_TRO_DOI_NGU))]


def _get_phan_anh(db: Session, phan_anh_id: str) -> PhanAnh:
    pa = db.get(PhanAnh, phan_anh_id)
    if pa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy phản ánh")
    return pa


@router.get("/{phan_anh_id}/comments", response_model=list[CommentOut])
def list_comments(phan_anh_id: str, db: DbDep, _: UserDep) -> list[CommentOut]:
    rows = liet_ke_binh_luan(db, phan_anh_id)
    return [
        CommentOut(
            id=b.id,
            noi_dung=b.noi_dung,
            la_phan_hoi_chinh_thuc=b.la_phan_hoi_chinh_thuc,
            vai_tro_nguoi_dang=b.vai_tro_nguoi_dang.value if b.vai_tro_nguoi_dang else None,
            created_at=b.created_at,
        )
        for b in rows
    ]


@router.post("/{phan_anh_id}/reply", response_model=FeedbackOut)
def reply(phan_anh_id: str, body: ReplyIn, db: DbDep, user: TeamDep) -> FeedbackOut:
    pa = _get_phan_anh(db, phan_anh_id)
    tra_loi_chinh_thuc(db, user, pa, body.noi_dung)
    db.commit()
    db.refresh(pa)
    return to_out(pa)


@router.patch("/{phan_anh_id}/status", response_model=FeedbackOut)
def change_status(phan_anh_id: str, body: StatusIn, db: DbDep, _: TeamDep) -> FeedbackOut:
    pa = _get_phan_anh(db, phan_anh_id)
    doi_trang_thai(db, pa, body.trang_thai)
    db.commit()
    db.refresh(pa)
    return to_out(pa)


class CommentIn(BaseModel):
    noi_dung: str


class GiaiQuyetIn(BaseModel):
    mo_ta_sua: str


class ThongBaoOut(BaseModel):
    id: str
    noi_dung: str
    da_doc: bool


@router.post("/{phan_anh_id}/comment", status_code=201)
def comment(phan_anh_id: str, body: CommentIn, db: DbDep, user: UserDep) -> dict[str, str]:
    pa = _get_phan_anh(db, phan_anh_id)
    bl = them_binh_luan(db, user, pa, body.noi_dung)
    db.commit()
    return {"id": bl.id, "trang_thai_kiem_duyet": bl.trang_thai_kiem_duyet.value}


@router.post("/{phan_anh_id}/dong-tinh")
def vote(phan_anh_id: str, db: DbDep, user: UserDep) -> dict[str, int]:
    pa = _get_phan_anh(db, phan_anh_id)
    so = dong_tinh(db, user, pa)
    db.commit()
    return {"so_dong_tinh": so}


@router.post("/{phan_anh_id}/giai-quyet-loi", response_model=FeedbackOut)
def giai_quyet(phan_anh_id: str, body: GiaiQuyetIn, db: DbDep, _: TeamDep) -> FeedbackOut:
    pa = _get_phan_anh(db, phan_anh_id)
    giai_quyet_loi(db, pa, body.mo_ta_sua)
    db.commit()
    db.refresh(pa)
    return to_out(pa)


@router.get("/thong-bao/cua-toi", response_model=list[ThongBaoOut])
def my_notifications(db: DbDep, user: UserDep) -> list[ThongBaoOut]:
    return [
        ThongBaoOut(id=t.id, noi_dung=t.noi_dung, da_doc=t.da_doc)
        for t in thong_bao_cua(db, user.id)
    ]
