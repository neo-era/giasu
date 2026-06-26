"""Nạp system prompt sản xuất từ thư mục `prompts/` (file `07_Bo_prompt_v1.0.md`).

KHÔNG nhúng nội dung prompt thẳng trong code. Loader + chèn biến ([LEVEL]…) +
cache + versioning.
"""

from app.personas.loader import (
    PersonaLoader,
    PromptError,
    PromptTemplate,
    get_persona_loader,
)

__all__ = [
    "PersonaLoader",
    "PromptError",
    "PromptTemplate",
    "get_persona_loader",
]
