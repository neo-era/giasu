import json
from typing import Any


def extract_json(text: str) -> dict[str, Any] | None:
    """Lấy object JSON đầu tiên trong text (model có thể kèm chữ/markdown thừa)."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None
