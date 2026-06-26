from app.models.enums import PhanKhuc
from app.personas import PersonaLoader
from app.tutor import directive_pham_vi


def test_dai_tra_co_nhac_pham_vi():
    d = directive_pham_vi(PhanKhuc.dai_tra)
    assert "Toán/Lí THPT" in d
    assert "từ chối" in d


def test_tinh_hoa_khong_gioi_han_o_day():
    assert directive_pham_vi(PhanKhuc.tinh_hoa) == ""


def test_prompt_thay_an_co_huong_dan_tu_choi():
    tpl = PersonaLoader().load("thay_an")
    assert "Ngoài phạm vi Toán/Lí THPT" in tpl.text
