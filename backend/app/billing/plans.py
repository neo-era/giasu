from app.models.enums import LoaiGoi

# Giới hạn câu/ngày theo gói (None = không giới hạn)
GIOI_HAN_NGAY: dict[LoaiGoi, int | None] = {
    LoaiGoi.free: 5,
    LoaiGoi.standard: 50,
    LoaiGoi.premium: None,
}

# Giá VND
GIA_VND: dict[LoaiGoi, int] = {
    LoaiGoi.free: 0,
    LoaiGoi.standard: 99_000,
    LoaiGoi.premium: 199_000,
}


def dung_bac_re(loai: LoaiGoi) -> bool:
    """Gói free luôn dùng bậc model rẻ (NFR-40)."""
    return loai == LoaiGoi.free
