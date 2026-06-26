from collections.abc import Iterator

from app.llm.base import ChatMessage, ChatResult, LLMProvider


class MockProvider(LLMProvider):
    """Nhà cung cấp giả lập — chạy offline cho dev/test, không gọi mạng."""

    name = "mock"

    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> ChatResult:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        text = f"[mock:{model}] {last_user}".strip()
        token_in = sum(len(m.content.split()) for m in messages)
        token_out = len(text.split())
        return ChatResult(
            text=text,
            model=model,
            provider=self.name,
            token_in=token_in,
            token_out=token_out,
        )

    def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> Iterator[str]:
        result = self.chat(messages, model, max_tokens=max_tokens, temperature=temperature)
        for word in result.text.split(" "):
            yield word + " "

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        # Vector giả định, xác định (deterministic) — đủ cho test pipeline RAG.
        return [[float(len(t)), float(sum(map(ord, t[:8]))), 0.0] for t in texts]
