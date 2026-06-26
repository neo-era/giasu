from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feedback.schemas import FeedbackCreate, FeedbackOut
from app.models import NguoiDung, PhanAnh
from app.models.enums import TrangThaiKiemDuyet, TrangThaiPhanAnh


def tao_phan_anh(db: Session, user: NguoiDung, body: FeedbackCreate) -> PhanAnh:
    # Luôn lưu người gửi (phục vụ kiểm duyệt/chống lạm dụng), nhưng ẩn khi hiển thị.
    pa = PhanAnh(
        nguoi_gui_id=user.id,
        an_danh=body.an_danh,
        chu_de=body.chu_de,
        tieu_de=body.tieu_de,
        noi_dung=body.noi_dung,
        anh_url=body.anh_url,
        loi_giai_id=body.loi_giai_id,
    )
    db.add(pa)
    db.flush()
    return pa


def to_out(pa: PhanAnh) -> FeedbackOut:
    return FeedbackOut(
        id=pa.id,
        chu_de=pa.chu_de,
        tieu_de=pa.tieu_de,
        noi_dung=pa.noi_dung,
        anh_url=pa.anh_url,
        trang_thai=pa.trang_thai,
        trang_thai_kiem_duyet=pa.trang_thai_kiem_duyet,
        so_dong_tinh=pa.so_dong_tinh,
        an_danh=pa.an_danh,
        nguoi_gui_id=None if pa.an_danh else pa.nguoi_gui_id,
        created_at=pa.created_at,
    )


def liet_ke(
    db: Session,
    *,
    chu_de=None,
    trang_thai: TrangThaiPhanAnh | None = None,
    sap_xep: str = "moi_nhat",
) -> list[PhanAnh]:
    stmt = select(PhanAnh).where(
        PhanAnh.trang_thai_kiem_duyet != TrangThaiKiemDuyet.chan  # ẩn nội dung bị chặn
    )
    if chu_de is not None:
        stmt = stmt.where(PhanAnh.chu_de == chu_de)
    if trang_thai is not None:
        stmt = stmt.where(PhanAnh.trang_thai == trang_thai)
    if sap_xep == "nhieu_dong_tinh":
        stmt = stmt.order_by(PhanAnh.so_dong_tinh.desc(), PhanAnh.created_at.desc())
    else:
        stmt = stmt.order_by(PhanAnh.created_at.desc())
    return list(db.scalars(stmt).all())
