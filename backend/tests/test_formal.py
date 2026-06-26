from app.formal.service import FormalResult, hinh_thuc_hoa
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockProvider

JSON_KHONG = (
    '{"hinh_thuc_hoa_duoc":false,"ly_do_neu_khong":"phát biểu mơ hồ",'
    '"phat_bieu_hinh_thuc":"","phac_thao_chien_luoc":[],'
    '"gia_thiet_can_lam_ro":[],"can_chuyen_chuyen_gia":true}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def test_khong_hinh_thuc_hoa_duoc():
    registry.reset_registry()
    registry.register_provider(_Scripted(JSON_KHONG))
    r = hinh_thuc_hoa("mệnh đề mơ hồ", LLMService(tiers={"reasoning": "scripted:m"}, backoff=0))
    assert r.hinh_thuc_hoa_duoc is False
    assert r.can_chuyen_chuyen_gia is True
    registry.reset_registry()


def test_khong_tu_nhan_dung():
    # Cấu trúc kết quả KHÔNG có trường khẳng định "đúng/chặt"
    fields = set(FormalResult.model_fields.keys())
    assert "dung" not in fields
    assert "chung_minh_dung" not in fields


def test_fallback_chuyen_chuyen_gia():
    registry.reset_registry()
    registry.register_provider(MockProvider())  # không phải JSON
    r = hinh_thuc_hoa("X", LLMService(tiers={"reasoning": "mock:m"}, backoff=0))
    assert r.hinh_thuc_hoa_duoc is False
    assert r.can_chuyen_chuyen_gia is True
    registry.reset_registry()
