"""Lớp trừu tượng nhà cung cấp LLM (FR-C12, NFR-30).

Mọi lời gọi model đi qua đây; khóa API chỉ đọc ở backend. Đổi model = đổi
config `llm_tiers`, KHÔNG sửa call-site.
"""

from app.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider
from app.llm.service import LLMService, get_llm_service
from app.llm.tiers import BacModel

__all__ = [
    "ChatMessage",
    "ChatResult",
    "LLMError",
    "LLMProvider",
    "LLMService",
    "get_llm_service",
    "BacModel",
]
