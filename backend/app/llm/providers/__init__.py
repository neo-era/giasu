"""Adapter các nhà cung cấp LLM. `init_default_providers` đăng ký mock luôn,
và đăng ký nhà cung cấp thật khi có khóa (đọc từ env)."""

from app.config import settings
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.mock import MockProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.registry import register_provider

__all__ = [
    "MockProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "init_default_providers",
]


def init_default_providers() -> None:
    register_provider(MockProvider())
    if settings.anthropic_api_key:
        register_provider(
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url,
            )
        )
    if settings.openai_api_key:
        register_provider(
            OpenAIProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        )
    if settings.gemini_api_key:
        # Gemini qua endpoint tương thích OpenAI → tái dùng OpenAIProvider, tên "gemini"
        register_provider(
            OpenAIProvider(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
                name="gemini",
            )
        )
