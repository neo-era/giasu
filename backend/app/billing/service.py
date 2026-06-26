import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.billing.plans import GIA_VND, GIOI_HAN_NGAY
from app.models import Goi, HanMuc, NguoiDung, ThanhToan
from app.models.enums import (
    LoaiGoi,
    PhuongThucThanhToan,
    TrangThaiGoi,
    TrangThaiThanhToan,
)

_VO_HAN = 10**9


class QuotaExceeded(Exception):
    """Vượt hạn mức câu/ngày của gói."""


def lay_goi_hien_tai(db: Session, user: NguoiDung) -> LoaiGoi:
    goi = db.scalar(
        select(Goi)
        .where(Goi.nguoi_dung_id == user.id, Goi.trang_thai == TrangThaiGoi.hoat_dong)
        .order_by(Goi.created_at.desc())
    )
    return goi.loai if goi else LoaiGoi.free


def _han_muc_hom_nay(db: Session, user: NguoiDung, loai: LoaiGoi) -> HanMuc:
    hom_nay = date.today()
    hm = db.scalar(select(HanMuc).where(HanMuc.nguoi_dung_id == user.id, HanMuc.ngay == hom_nay))
    if hm is None:
        gioi_han = GIOI_HAN_NGAY.get(loai)
        hm = HanMuc(
            nguoi_dung_id=user.id,
            ngay=hom_nay,
            so_cau_da_dung=0,
            gioi_han=gioi_han if gioi_han is not None else _VO_HAN,
        )
        db.add(hm)
        db.flush()
    return hm


def kiem_va_dung_luot(db: Session, user: NguoiDung) -> None:
    """Tăng 1 lượt dùng trong ngày; vượt giới hạn gói → QuotaExceeded."""
    loai = lay_goi_hien_tai(db, user)
    if GIOI_HAN_NGAY.get(loai) is None:  # gói không giới hạn
        return
    hm = _han_muc_hom_nay(db, user, loai)
    if hm.so_cau_da_dung >= hm.gioi_han:
        raise QuotaExceeded("Đã hết lượt hỏi trong ngày của gói hiện tại")
    hm.so_cau_da_dung += 1
    db.flush()


def da_dung_hom_nay(db: Session, user: NguoiDung) -> int:
    hm = db.scalar(
        select(HanMuc).where(HanMuc.nguoi_dung_id == user.id, HanMuc.ngay == date.today())
    )
    return hm.so_cau_da_dung if hm else 0


def tao_checkout(db: Session, user: NguoiDung, loai_goi: LoaiGoi) -> ThanhToan:
    if loai_goi == LoaiGoi.free:
        raise ValueError("Gói free không cần thanh toán")
    tt = ThanhToan(
        nguoi_dung_id=user.id,
        so_tien=GIA_VND[loai_goi],
        phuong_thuc=PhuongThucThanhToan.vietqr,
        trang_thai=TrangThaiThanhToan.cho,
        ma_giao_dich=uuid.uuid4().hex,
        goi_muon=loai_goi,
    )
    db.add(tt)
    db.commit()
    db.refresh(tt)
    return tt


def vietqr_payload(tt: ThanhToan) -> str:
    """Chuỗi nội dung QR (stub) — tích hợp ngân hàng thật sau."""
    return f"VIETQR|BANK|ACCOUNT|{tt.so_tien}|{tt.ma_giao_dich}"


def xac_nhan_thanh_toan(db: Session, ma_giao_dich: str) -> ThanhToan | None:
    """Xác nhận giao dịch (webhook). IDEMPOTENT theo ma_giao_dich."""
    tt = db.scalar(select(ThanhToan).where(ThanhToan.ma_giao_dich == ma_giao_dich))
    if tt is None:
        return None
    if tt.trang_thai == TrangThaiThanhToan.thanh_cong:
        return tt  # đã xử lý → không nâng cấp lần nữa
    tt.trang_thai = TrangThaiThanhToan.thanh_cong
    if tt.goi_muon is not None:
        db.add(
            Goi(
                nguoi_dung_id=tt.nguoi_dung_id,
                loai=tt.goi_muon,
                trang_thai=TrangThaiGoi.hoat_dong,
            )
        )
    db.commit()
    return tt
