from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockProvider
from app.translate.service import dich

JSON_DICH = (
    '{"ban_dich":"Cho $x^2+1=0$. Giải.","thuat_ngu":[{"goc":"equation","viet":"phương trình"}],'
    '"cho_khong_chac":["câu 2 nhập nhằng"],"do_tin_cay":0.7}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def test_dich_giu_cong_thuc_va_gan_co():
    registry.reset_registry()
    registry.register_provider(_Scripted(JSON_DICH))
    r = dich("Soit $x^2+1=0$.", LLMService(tiers={"can_bang": "scripted:m"}, backoff=0))
    assert "$x^2+1=0$" in r.ban_dich  # công thức giữ nguyên
    assert r.cho_khong_chac  # chỗ nhập nhằng được gắn cờ
    registry.reset_registry()


def test_fallback_gan_co_can_ra():
    registry.reset_registry()
    registry.register_provider(MockProvider())
    r = dich("text", LLMService(tiers={"can_bang": "mock:m"}, backoff=0))
    assert r.cho_khong_chac  # không dịch được → gắn cờ cần người rà
    registry.reset_registry()
