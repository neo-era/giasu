import httpx

from app.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider


class AnthropicProvider(LLMProvider):
    """Adapter Anthropic Messages API. Khóa giữ riêng tư, không lộ ra ngoài."""

    name = "anthropic"
    _ANTHROPIC_VERSION = "2023-06-01"

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com") -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def __repr__(self) -> str:  # KHÔNG in khóa (NFR-30)
        return f"AnthropicProvider(base_url={self._base_url!r}, api_key='***')"

    def _content_blocks(self, m: ChatMessage) -> list[dict] | str:
        if not m.images:
            return m.content
        blocks: list[dict] = [{"type": "text", "text": m.content}]
        for url in m.images:
            blocks.append({"type": "image", "source": {"type": "url", "url": url}})
        return blocks

    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> ChatResult:
        system = " ".join(m.content for m in messages if m.role == "system") or None
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": m.role, "content": self._content_blocks(m)}
                for m in messages
                if m.role != "system"
            ],
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self._ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        try:
            resp = httpx.post(
                f"{self._base_url}/v1/messages",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
        except httpx.HTTPError as exc:
            raise LLMError(f"Anthropic kết nối lỗi: {type(exc).__name__}") from exc
        if resp.status_code >= 400:
            # Thông báo lỗi của Anthropic KHÔNG chứa khóa → an toàn để nêu
            try:
                msg = resp.json().get("error", {}).get("message", "")
            except ValueError:
                msg = resp.text[:200]
            raise LLMError(f"Anthropic {resp.status_code}: {msg}")
        data = resp.json()

        text = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        usage = data.get("usage", {})
        return ChatResult(
            text=text,
            model=data.get("model", model),
            provider=self.name,
            token_in=usage.get("input_tokens", 0),
            token_out=usage.get("output_tokens", 0),
        )
