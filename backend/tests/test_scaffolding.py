from app.models.enums import MucDoHoc
from app.scaffolding import MucHoTro, directive_ho_tro, tinh_muc_ho_tro


def test_yeu_bat_dau_giai_mau():
    assert tinh_muc_ho_tro(MucDoHoc.yeu) == MucHoTro.giai_mau


def test_yeu_tien_bo_thi_giam_dan():
    # 0 đúng → giải mẫu; 3 đúng → gợi ý; 6 đúng → socratic (fading)
    assert tinh_muc_ho_tro(MucDoHoc.yeu, so_dung_lien_tiep=0) == MucHoTro.giai_mau
    assert tinh_muc_ho_tro(MucDoHoc.yeu, so_dung_lien_tiep=3) == MucHoTro.goi_y_tung_buoc
    assert tinh_muc_ho_tro(MucDoHoc.yeu, so_dung_lien_tiep=6) == MucHoTro.socratic


def test_gioi_khong_bi_ep_giai_mau():
    # Dù sai nhiều, HS giỏi không bao giờ bị ép giải mẫu (trần = gợi ý)
    assert tinh_muc_ho_tro(MucDoHoc.kha_gioi) == MucHoTro.socratic
    assert tinh_muc_ho_tro(MucDoHoc.kha_gioi, so_sai_lien_tiep=10) == MucHoTro.goi_y_tung_buoc


def test_trung_binh_sai_thi_tang_ho_tro():
    assert tinh_muc_ho_tro(MucDoHoc.trung_binh) == MucHoTro.goi_y_tung_buoc
    assert tinh_muc_ho_tro(MucDoHoc.trung_binh, so_sai_lien_tiep=2) == MucHoTro.giai_mau


def test_directive_co_noi_dung():
    assert "giải mẫu" in directive_ho_tro(MucHoTro.giai_mau)
    assert "Socratic" in directive_ho_tro(MucHoTro.socratic)
