from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feedback.schemas import FeedbackCreate, FeedbackOut
from app.models import (
    BinhLuan,
    BoHoiQuy,
    DongTinh,
    HangDoiDuyet,
    NguoiDung,
    PhanAnh,
    ThongBao,
)
from app.models.enums import (
    ChuDePhanAnh,
    TrangThaiKiemDuyet,
    TrangThaiPhanAnh,
    VaiTro,
)
from app.moderation.pii import che_thong_tin_ca_nhan
from app.moderation.service import classify_text

# Vai trò "đội ngũ" được trả lời/đổi trạng thái/kiểm duyệt (FR-F07)
VAI_TRO_DOI_NGU = (VaiTro.bien_tap, VaiTro.quan_tri, VaiTro.hlv)


def tao_phan_anh(db: Session, user: NguoiDung, body: FeedbackCreate) -> PhanAnh:
    # NFR-33: kiểm duyệt server-side TRƯỚC khi lưu/hiển thị (không tin client).
    # 1) Che thông tin cá nhân bằng regex tất định.
    tieu_de, _ = che_thong_tin_ca_nhan(body.tieu_de)
    noi_dung, _ = che_thong_tin_ca_nhan(body.noi_dung)
    # 2) Phân loại độc hại/spam bằng P9.
    kq = classify_text(noi_dung)

    # Luôn lưu người gửi (phục vụ kiểm duyệt/chống lạm dụng), nhưng ẩn khi hiển thị.
    pa = PhanAnh(
        nguoi_gui_id=user.id,
        an_danh=body.an_danh,
        chu_de=body.chu_de,
        tieu_de=tieu_de,
        noi_dung=noi_dung,
        anh_url=body.anh_url,
        loi_giai_id=body.loi_giai_id,
        trang_thai_kiem_duyet=kq.quyet_dinh,
    )
    db.add(pa)
    db.flush()
    # F09: phản ánh "lỗi lời giải" → đẩy vào hàng đợi rà soát của lớp kiểm chứng
    if body.chu_de == ChuDePhanAnh.loi_loi_giai:
        db.add(
            HangDoiDuyet(
                loai="phan_anh_loi",
                noi_dung=pa.tieu_de,
                chi_tiet={"phan_anh_id": pa.id, "loi_giai_id": pa.loi_giai_id},
            )
        )
        db.flush()
    return pa


def them_binh_luan(db: Session, user: NguoiDung, phan_anh: PhanAnh, noi_dung: str) -> BinhLuan:
    """Bình luận cộng đồng (FR-F03) — có kiểm duyệt như nội dung người dùng."""
    noi_dung, _ = che_thong_tin_ca_nhan(noi_dung)
    kq = classify_text(noi_dung)
    bl = BinhLuan(
        phan_anh_id=phan_anh.id,
        nguoi_dang_id=user.id,
        vai_tro_nguoi_dang=user.vai_tro,
        la_phan_hoi_chinh_thuc=False,
        noi_dung=noi_dung,
        trang_thai_kiem_duyet=kq.quyet_dinh,
    )
    db.add(bl)
    db.flush()
    return bl


def dong_tinh(db: Session, user: NguoiDung, phan_anh: PhanAnh) -> int:
    """'Tôi cũng gặp' (FR-F04) — mỗi người tối đa 1 lần."""
    da_co = db.scalar(
        select(DongTinh).where(
            DongTinh.nguoi_dung_id == user.id, DongTinh.phan_anh_id == phan_anh.id
        )
    )
    if da_co is None:
        db.add(DongTinh(nguoi_dung_id=user.id, phan_anh_id=phan_anh.id))
        phan_anh.so_dong_tinh += 1
        db.flush()
    return phan_anh.so_dong_tinh


def giai_quyet_loi(db: Session, phan_anh: PhanAnh, mo_ta_sua: str) -> BoHoiQuy:
    """Sửa xong lỗi lời giải → cập nhật phản ánh + bổ sung bộ hồi quy + thông báo
    người gửi (FR-F09/F10, UC-04)."""
    phan_anh.trang_thai = TrangThaiPhanAnh.da_tra_loi
    hq = BoHoiQuy(nguon_phan_anh_id=phan_anh.id, mo_ta=mo_ta_sua, nhan="loi_loi_giai")
    db.add(hq)
    if phan_anh.nguoi_gui_id:
        db.add(
            ThongBao(
                nguoi_dung_id=phan_anh.nguoi_gui_id,
                noi_dung=f"Phản ánh '{phan_anh.tieu_de}' đã được xử lý và bổ sung kiểm chứng.",
            )
        )
    db.flush()
    return hq


def thong_bao_cua(db: Session, nguoi_dung_id: str) -> list[ThongBao]:
    return list(
        db.scalars(
            select(ThongBao)
            .where(ThongBao.nguoi_dung_id == nguoi_dung_id)
            .order_by(ThongBao.created_at.desc())
        ).all()
    )


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
    # Chỉ hiển thị nội dung đã cho phép hoặc chờ duyệt mặc định; ẩn nội dung bị
    # chặn VÀ nội dung đang chờ người duyệt (FR-F08).
    stmt = select(PhanAnh).where(
        PhanAnh.trang_thai_kiem_duyet.notin_(
            (TrangThaiKiemDuyet.chan, TrangThaiKiemDuyet.can_nguoi_duyet)
        )
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
