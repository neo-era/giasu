from app.llm.base import LLMError, LLMProvider

_providers: dict[str, LLMProvider] = {}


def register_provider(provider: LLMProvider) -> None:
    _providers[provider.name] = provider


def get_provider(name: str) -> LLMProvider:
    if name not in _providers:
        raise LLMError(f"Nhà cung cấp LLM chưa đăng ký: {name}")
    return _providers[name]


def has_provider(name: str) -> bool:
    return name in _providers


def reset_registry() -> None:
    _providers.clear()
