import pytest

from app.llm import BacModel, ChatMessage, ChatResult, LLMError, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.mock import MockProvider


@pytest.fixture(autouse=True)
def clean_registry():
    registry.reset_registry()
    registry.register_provider(MockProvider())
    yield
    registry.reset_registry()


def _msgs() -> list[ChatMessage]:
    return [ChatMessage(role="user", content="2+2 bằng mấy")]


def test_goi_qua_bac_tra_mock():
    svc = LLMService(tiers={"re": "mock:mock-fast"}, backoff=0)
    r = svc.complete(BacModel.re, _msgs())
    assert r.provider == "mock"
    assert r.model == "mock-fast"
    assert "2+2" in r.text
    assert r.token_in > 0 and r.token_out > 0


def test_doi_config_model_khong_doi_callsite():
    msgs = _msgs()
    svc1 = LLMService(tiers={"reasoning": "mock:opus-4.8"}, backoff=0)
    svc2 = LLMService(tiers={"reasoning": "mock:sonnet-4.6"}, backoff=0)
    # Call-site y hệt; chỉ khác config → model trả về khác (FR-C12)
    assert svc1.complete(BacModel.reasoning, msgs).model == "opus-4.8"
    assert svc2.complete(BacModel.reasoning, msgs).model == "sonnet-4.6"


class _FlakyProvider(LLMProvider):
    name = "flaky"

    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def chat(self, messages, model, **kw) -> ChatResult:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise LLMError("tạm lỗi")
        return ChatResult(text="ok", model=model, provider=self.name)


def test_retry_thanh_cong():
    flaky = _FlakyProvider(fail_times=2)
    registry.register_provider(flaky)
    svc = LLMService(tiers={"re": "flaky:m"}, max_retries=2, backoff=0)
    assert svc.complete(BacModel.re, _msgs()).text == "ok"
    assert flaky.calls == 3


def test_suy_giam_diu_fallback():
    registry.register_provider(_FlakyProvider(fail_times=99))
    svc = LLMService(
        tiers={"reasoning": "flaky:m", "re": "mock:mock-fast"},
        max_retries=1,
        backoff=0,
        fallback_tier="re",
    )
    # Bậc reasoning lỗi hẳn → suy giảm dịu xuống bậc 're' (NFR-21)
    assert svc.complete(BacModel.reasoning, _msgs()).provider == "mock"


def test_tat_ca_loi_thi_raise():
    registry.register_provider(_FlakyProvider(fail_times=99))
    svc = LLMService(tiers={"reasoning": "flaky:m"}, max_retries=1, backoff=0)
    with pytest.raises(LLMError):
        svc.complete(BacModel.reasoning, _msgs())


def test_khong_lo_khoa_trong_repr():
    p = AnthropicProvider(api_key="sk-super-secret-123")
    assert "sk-super-secret-123" not in repr(p)
    assert "super-secret" not in repr(p)
    assert "***" in repr(p)


def test_stream_mock():
    svc = LLMService(tiers={"re": "mock:mock-fast"}, backoff=0)
    out = "".join(svc.stream(BacModel.re, _msgs()))
    assert out.strip().startswith("[mock:mock-fast]")
