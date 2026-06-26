import time
from collections.abc import Iterator
from functools import lru_cache

from app.config import settings
from app.llm.base import ChatMessage, ChatResult, LLMError
from app.llm.registry import get_provider
from app.llm.tiers import BacModel


def _tier_key(tier: BacModel | str) -> str:
    return tier.value if isinstance(tier, BacModel) else str(tier)


class LLMService:
    """Định tuyến theo BẬC + retry/timeout + suy giảm dịu (FR-C07/C12, NFR-21).

    Call-site chỉ truyền BẬC (re/can_bang/reasoning/vision); model thực do
    config `llm_tiers` quyết định — đổi model không cần sửa call-site.
    """

    def __init__(
        self,
        tiers: dict[str, str] | None = None,
        *,
        timeout: float | None = None,
        max_retries: int | None = None,
        backoff: float | None = None,
        fallback_tier: str | None = None,
    ) -> None:
        self.tiers = dict(tiers) if tiers is not None else dict(settings.llm_tiers)
        self.timeout = timeout if timeout is not None else settings.llm_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.llm_max_retries
        self.backoff = backoff if backoff is not None else settings.llm_retry_backoff
        self.fallback_tier = (
            fallback_tier if fallback_tier is not None else settings.llm_fallback_tier
        )

    def resolve(self, tier: BacModel | str) -> tuple[str, str]:
        """Trả (provider, model) của một bậc — dùng để ghi model khi stream."""
        return self._resolve(tier)

    def _resolve(self, tier: BacModel | str) -> tuple[str, str]:
        key = _tier_key(tier)
        if key not in self.tiers:
            raise LLMError(f"Bậc model không có trong cấu hình: {key}")
        spec = self.tiers[key]
        if ":" not in spec:
            raise LLMError(f"Cấu hình bậc sai định dạng (provider:model): {spec}")
        provider_name, model = spec.split(":", 1)
        return provider_name, model

    def _attempt(self, tier: BacModel | str, messages: list[ChatMessage], **kw) -> ChatResult:
        provider_name, model = self._resolve(tier)
        provider = get_provider(provider_name)
        last_exc: LLMError | None = None
        for i in range(self.max_retries + 1):
            try:
                return provider.chat(messages, model, timeout=self.timeout, **kw)
            except LLMError as exc:
                last_exc = exc
                if i < self.max_retries and self.backoff:
                    time.sleep(self.backoff * (2**i))
        raise last_exc  # pragma: no cover (luôn có last_exc khi tới đây)

    def complete(self, tier: BacModel | str, messages: list[ChatMessage], **kw) -> ChatResult:
        tiers_to_try: list[BacModel | str] = [tier]
        if self.fallback_tier and _tier_key(tier) != self.fallback_tier:
            tiers_to_try.append(self.fallback_tier)

        last_exc: LLMError | None = None
        for t in tiers_to_try:
            try:
                return self._attempt(t, messages, **kw)
            except LLMError as exc:
                last_exc = exc
        raise LLMError(f"Tất cả bậc model đều lỗi: {last_exc}")

    def stream(self, tier: BacModel | str, messages: list[ChatMessage], **kw) -> Iterator[str]:
        provider_name, model = self._resolve(tier)
        provider = get_provider(provider_name)
        yield from provider.stream_chat(messages, model, timeout=self.timeout, **kw)


@lru_cache
def get_llm_service() -> LLMService:
    """Singleton dùng trong app; đảm bảo các nhà cung cấp mặc định đã đăng ký.

    Dùng ánh xạ bậc từ runtime_config để quản trị đổi model không cần deploy
    lại (gọi get_llm_service.cache_clear() sau khi đổi cấu hình)."""
    from app.llm.providers import init_default_providers
    from app.runtime_config import get_tiers

    init_default_providers()
    return LLMService(tiers=get_tiers())
