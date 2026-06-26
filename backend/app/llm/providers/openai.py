import httpx

from app.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider


class OpenAIProvider(LLMProvider):
    """Adapter OpenAI-compatible (/chat/completions). Dùng được cho các API
    tương thích OpenAI. Khóa giữ riêng tư, không lộ ra ngoài."""

    name = "openai"

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def __repr__(self) -> str:  # KHÔNG in khóa (NFR-30)
        return f"OpenAIProvider(base_url={self._base_url!r}, api_key='***')"

    def _content(self, m: ChatMessage) -> list[dict] | str:
        if not m.images:
            return m.content
        parts: list[dict] = [{"type": "text", "text": m.content}]
        for url in m.images:
            parts.append({"type": "image_url", "image_url": {"url": url}})
        return parts

    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> ChatResult:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": m.role, "content": self._content(m)} for m in messages],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "content-type": "application/json",
        }
        try:
            resp = httpx.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            raise LLMError(f"OpenAI request lỗi: {type(exc).__name__}") from exc

        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return ChatResult(
            text=text,
            model=data.get("model", model),
            provider=self.name,
            token_in=usage.get("prompt_tokens", 0),
            token_out=usage.get("completion_tokens", 0),
        )
