from app.chat.service import build_system_prompt
from app.models.enums import CheDoTraLoi
from app.tutor import directive_che_do


def test_mac_dinh_goi_y_khong_giai_ho():
    d = directive_che_do(CheDoTraLoi.goi_y, da_qua_cong_no_luc=False)
    assert "GỢI Ý" in d
    assert "KHÔNG trình bày lời giải đầy đủ" in d


def test_xin_loi_giai_nhung_chua_qua_cong():
    # Yêu cầu lời giải đầy đủ nhưng chưa qua cổng nỗ lực → vẫn gợi ý
    d = directive_che_do(CheDoTraLoi.loi_giai_day_du, da_qua_cong_no_luc=False)
    assert "CHƯA qua cổng nỗ lực" in d
    assert "CHƯA trình bày lời giải đầy đủ" in d


def test_qua_cong_thi_duoc_loi_giai():
    d = directive_che_do(CheDoTraLoi.loi_giai_day_du, da_qua_cong_no_luc=True)
    assert "được phép trình bày" in d


def test_build_system_prompt_co_chi_dan():
    system = build_system_prompt(
        "thay_an", "trung_binh", directive_che_do(CheDoTraLoi.goi_y, False)
    )
    assert "Thầy An" in system
    assert "GỢI Ý" in system  # chỉ dẫn chế độ được nối vào system prompt
