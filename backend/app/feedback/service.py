from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feedback.schemas import FeedbackCreate, FeedbackOut
from app.models import BinhLuan, NguoiDung, PhanAnh
from app.models.enums import (
    TrangThaiKiemDuyet,
    TrangThaiPhanAnh,
    VaiTro,
)

# Vai trò "đội ngũ" được trả lời/đổi trạng thái/kiểm duyệt (FR-F07)
VAI_TRO_DOI_NGU = (VaiTro.bien_tap, VaiTro.quan_tri, VaiTro.hlv)


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


def tra_loi_chinh_thuc(db: Session, user: NguoiDung, phan_anh: PhanAnh, noi_dung: str) -> BinhLuan:
    """Đội ngũ trả lời chính thức → tự chuyển trạng thái 'Đã trả lời' (FR-F05/F06)."""
    bl = BinhLuan(
        phan_anh_id=phan_anh.id,
        nguoi_dang_id=user.id,
        vai_tro_nguoi_dang=user.vai_tro,
        la_phan_hoi_chinh_thuc=True,
        noi_dung=noi_dung,
        trang_thai_kiem_duyet=TrangThaiKiemDuyet.cho_phep,  # đội ngũ → tin cậy
    )
    db.add(bl)
    phan_anh.trang_thai = TrangThaiPhanAnh.da_tra_loi
    db.flush()
    return bl


def doi_trang_thai(db: Session, phan_anh: PhanAnh, trang_thai: TrangThaiPhanAnh) -> None:
    phan_anh.trang_thai = trang_thai
    db.flush()


def liet_ke_binh_luan(db: Session, phan_anh_id: str) -> list[BinhLuan]:
    return list(
        db.scalars(
            select(BinhLuan)
            .where(
                BinhLuan.phan_anh_id == phan_anh_id,
                BinhLuan.trang_thai_kiem_duyet != TrangThaiKiemDuyet.chan,
            )
            .order_by(BinhLuan.created_at)
        ).all()
    )
