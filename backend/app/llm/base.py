from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field


class LLMError(Exception):
    """Lỗi tầng LLM. KHÔNG được chứa khóa API trong thông điệp."""


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str
    images: list[str] | None = None  # URL hoặc data URI base64 (vision)


@dataclass
class ChatResult:
    text: str
    model: str
    provider: str
    token_in: int = 0
    token_out: int = 0
    meta: dict = field(default_factory=dict)  # KHÔNG đặt khóa API vào đây


class LLMProvider(ABC):
    """Giao diện chung cho mọi nhà cung cấp. Adapter cụ thể hiện thực `chat`."""

    name: str = "base"

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> ChatResult: ...

    def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: float | None = None,
    ) -> Iterator[str]:
        """Mặc định: phát toàn bộ kết quả một lần. Adapter có thể override SSE."""
        yield self.chat(
            messages,
            model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        ).text

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        raise NotImplementedError(f"{self.name} chưa hỗ trợ embeddings")
