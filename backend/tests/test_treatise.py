import pytest

from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.treatise.service import ChuaDuyetError, bien_tap

JSON_CL = (
    '{"tieu_de":"Về số nguyên tố","cau_truc":['
    '{"loai":"dinh_ly","so":0,"noi_dung_latex":"Có vô hạn số nguyên tố"},'
    '{"loai":"chung_minh","so":0,"noi_dung_latex":"Giả sử hữu hạn..."},'
    '{"loai":"dinh_ly","so":0,"noi_dung_latex":"Định lý 2"}],'
    '"tom_tat":"abstract","tai_lieu_tham_khao":["Euclid"]}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def test_chua_duyet_thi_tu_choi():
    with pytest.raises(ChuaDuyetError):
        bien_tap("nội dung", da_duyet=False)


def test_danh_so_dinh_ly_nhat_quan():
    registry.reset_registry()
    registry.register_provider(_Scripted(JSON_CL))
    cl = bien_tap(
        "đã duyệt", da_duyet=True, llm=LLMService(tiers={"reasoning": "scripted:m"}, backoff=0)
    )
    dinh_ly = [m for m in cl.cau_truc if m.loai == "dinh_ly"]
    assert [m.so for m in dinh_ly] == [1, 2]  # tự đánh số nhất quán
    registry.reset_registry()
