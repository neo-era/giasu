from app.models.enums import PhamViKiemChung, PhuongPhapKiemChung, TrangThaiKiemChung
from app.verify import (
    danh_dau_khai_niem,
    kiem_bien_doi,
    kiem_dao_ham,
    kiem_gia_tri_so,
    kiem_nghiem,
    kiem_tich_phan,
    luu_ket_qua,
)


# ---- Biến đổi đại số ----
def test_bien_doi_dung():
    r = kiem_bien_doi("(x+1)^2", "x^2 + 2x + 1")
    assert r.trang_thai == TrangThaiKiemChung.dung
    assert r.pham_vi_da_kiem == PhamViKiemChung.tinh_toan


def test_bien_doi_sai_bi_bat():
    # Lời giải sai bị tiêm: (x+1)^2 ≠ x^2 + 1
    r = kiem_bien_doi("(x+1)^2", "x^2 + 1")
    assert r.trang_thai == TrangThaiKiemChung.sai


# ---- Nghiệm phương trình ----
def test_nghiem_dung():
    r = kiem_nghiem("x^2 - 1 = 0", ["1", "-1"])
    assert r.trang_thai == TrangThaiKiemChung.dung


def test_nghiem_thieu_bi_bat():
    r = kiem_nghiem("x^2 - 1 = 0", ["1"])  # thiếu nghiệm -1
    assert r.trang_thai == TrangThaiKiemChung.sai
    assert "-1" in r.chi_tiet["thieu"]


def test_nghiem_thua_bi_bat():
    r = kiem_nghiem("x^2 - 1 = 0", ["1", "-1", "2"])  # nghiệm 2 thừa
    assert r.trang_thai == TrangThaiKiemChung.sai
    assert "2" in r.chi_tiet["thua"]


# ---- Đạo hàm ----
def test_dao_ham_dung():
    assert kiem_dao_ham("x^2", "2*x").trang_thai == TrangThaiKiemChung.dung


def test_dao_ham_sai_bi_bat():
    assert kiem_dao_ham("x^2", "x").trang_thai == TrangThaiKiemChung.sai


# ---- Tích phân ----
def test_tich_phan_bat_dinh_dung():
    # ∫ 2x dx = x^2 (+C) — so qua đạo hàm
    assert kiem_tich_phan("2*x", "x^2").trang_thai == TrangThaiKiemChung.dung


def test_tich_phan_xac_dinh_dung():
    # ∫_0^1 2x dx = 1
    r = kiem_tich_phan("2*x", "1", can_duoi="0", can_tren="1")
    assert r.trang_thai == TrangThaiKiemChung.dung


def test_tich_phan_sai_bi_bat():
    assert kiem_tich_phan("2*x", "x^3").trang_thai == TrangThaiKiemChung.sai


# ---- Giá trị số ----
def test_gia_tri_so_dung():
    assert kiem_gia_tri_so("3*4 + 2", 14).trang_thai == TrangThaiKiemChung.dung


# ---- Trung thực phạm vi (FR-L08) ----
def test_danh_dau_khai_niem_khong_khang_dinh():
    r = danh_dau_khai_niem("Chứng minh bằng quy nạp — cần người duyệt")
    assert r.pham_vi_da_kiem == PhamViKiemChung.khai_niem
    assert r.trang_thai == TrangThaiKiemChung.khong_du_can_cu


# ---- Ghi DB ----
def test_luu_ket_qua_ghi_db(session):
    r = kiem_bien_doi("(x+1)^2", "x^2 + 2x + 1")
    kq = luu_ket_qua(session, r)
    session.commit()
    assert kq.id
    assert kq.phuong_phap == PhuongPhapKiemChung.sympy
    assert kq.pham_vi_da_kiem == PhamViKiemChung.tinh_toan
    assert kq.can_nguoi_duyet is False  # tính toán đúng → không cần duyệt


def test_luu_khai_niem_can_nguoi_duyet(session):
    kq = luu_ket_qua(session, danh_dau_khai_niem("lập luận"))
    session.commit()
    assert kq.can_nguoi_duyet is True  # khái niệm → chuyển người duyệt
