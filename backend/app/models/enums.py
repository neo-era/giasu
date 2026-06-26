import enum


class VaiTro(str, enum.Enum):
    hoc_sinh = "hoc_sinh"
    phu_huynh = "phu_huynh"
    hlv = "hlv"  # huấn luyện viên / giáo viên duyệt (tinh hoa)
    bien_tap = "bien_tap"
    quan_tri = "quan_tri"


class TrangThaiNguoiDung(str, enum.Enum):
    cho_xac_thuc = "cho_xac_thuc"
    hoat_dong = "hoat_dong"
    khoa = "khoa"


class PhanKhuc(str, enum.Enum):
    dai_tra = "dai_tra"
    tinh_hoa = "tinh_hoa"


class MucDoHoc(str, enum.Enum):
    """Mức scaffolding theo trình độ (FR-L01/L02)."""

    yeu = "yeu"
    trung_binh = "trung_binh"
    kha_gioi = "kha_gioi"


class VaiTinNhan(str, enum.Enum):
    nguoi_dung = "nguoi_dung"
    tro_ly = "tro_ly"
    he_thong = "he_thong"


class CapDo(str, enum.Enum):
    thpt = "thpt"
    olympiad = "olympiad"


class DoKho(str, enum.Enum):
    nhan_biet = "nhan_biet"
    thong_hieu = "thong_hieu"
    van_dung = "van_dung"
    van_dung_cao = "van_dung_cao"


class PhuongPhapKiemChung(str, enum.Enum):
    sympy = "sympy"
    rag = "rag"
    cross_check = "cross_check"
    proof = "proof"
    nguoi = "nguoi"


class TrangThaiKiemChung(str, enum.Enum):
    dung = "dung"
    nghi_van = "nghi_van"
    sai = "sai"
    khong_du_can_cu = "khong_du_can_cu"


class PhamViKiemChung(str, enum.Enum):
    """Phạm vi 'đã kiểm chứng' trung thực (FR-L08, mục 3.4 SRS)."""

    tinh_toan = "tinh_toan"
    khai_niem = "khai_niem"


class LoaiGoi(str, enum.Enum):
    free = "free"
    standard = "standard"
    premium = "premium"


class TrangThaiGoi(str, enum.Enum):
    hoat_dong = "hoat_dong"
    het_han = "het_han"
    huy = "huy"


class PhuongThucThanhToan(str, enum.Enum):
    vietqr = "vietqr"
    momo = "momo"
    zalopay = "zalopay"
    vnpay = "vnpay"


class TrangThaiThanhToan(str, enum.Enum):
    cho = "cho"
    thanh_cong = "thanh_cong"
    that_bai = "that_bai"


class ChuDePhanAnh(str, enum.Enum):
    loi_loi_giai = "loi_loi_giai"
    gop_y = "gop_y"
    thanh_toan = "thanh_toan"
    trai_nghiem = "trai_nghiem"
    khac = "khac"


class TrangThaiPhanAnh(str, enum.Enum):
    moi = "moi"
    dang_xu_ly = "dang_xu_ly"
    da_tra_loi = "da_tra_loi"
    da_dong = "da_dong"


class CheDoTraLoi(str, enum.Enum):
    """Chế độ trả lời của gia sư (FR-M01/L03): mặc định chỉ gợi ý."""

    goi_y = "goi_y"
    loi_giai_day_du = "loi_giai_day_du"


class MucDichOTP(str, enum.Enum):
    dang_ky = "dang_ky"
    dang_nhap = "dang_nhap"


class TrangThaiKiemDuyet(str, enum.Enum):
    """Kiểm duyệt nội dung người dùng (FR-F08, NFR-33)."""

    cho_duyet = "cho_duyet"
    cho_phep = "cho_phep"
    can_nguoi_duyet = "can_nguoi_duyet"
    chan = "chan"
