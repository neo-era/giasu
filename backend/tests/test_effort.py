from app.effort import (
    GIOI_HAN_GOI_Y,
    NGUONG_NO_LUC,
    TrangThaiNoLuc,
    con_duoc_goi_y,
    da_qua_cong_no_luc,
)
from app.models.enums import CheDoTraLoi


def test_chua_thu_du_thi_khong_mo_loi_giai():
    # Lượt đầu xin lời giải đầy đủ → CHƯA qua cổng
    state = TrangThaiNoLuc(so_luot_hs=1, so_goi_y_da_dung=0)
    assert da_qua_cong_no_luc(state, CheDoTraLoi.loi_giai_day_du) is False


def test_thu_du_thi_mo_loi_giai():
    state = TrangThaiNoLuc(so_luot_hs=NGUONG_NO_LUC, so_goi_y_da_dung=1)
    assert da_qua_cong_no_luc(state, CheDoTraLoi.loi_giai_day_du) is True


def test_che_do_goi_y_khong_bao_gio_mo_loi_giai():
    # Dù đã thử nhiều, nếu không yêu cầu rõ chế độ lời giải → vẫn không mở
    state = TrangThaiNoLuc(so_luot_hs=99, so_goi_y_da_dung=0)
    assert da_qua_cong_no_luc(state, CheDoTraLoi.goi_y) is False


def test_khong_moi_duoc_dap_an_bang_dien_dat():
    # Cổng chỉ phụ thuộc trạng thái nỗ lực, KHÔNG phụ thuộc câu chữ của HS.
    # Lượt đầu (chưa thử) → mọi yêu cầu đều bị chặn mở lời giải.
    state = TrangThaiNoLuc(so_luot_hs=1, so_goi_y_da_dung=0)
    for che_do in (CheDoTraLoi.goi_y, CheDoTraLoi.loi_giai_day_du):
        assert da_qua_cong_no_luc(state, che_do) is False


def test_tiet_che_goi_y():
    assert con_duoc_goi_y(TrangThaiNoLuc(1, GIOI_HAN_GOI_Y - 1)) is True
    assert con_duoc_goi_y(TrangThaiNoLuc(1, GIOI_HAN_GOI_Y)) is False
