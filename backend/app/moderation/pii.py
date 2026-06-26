import re

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# SĐT VN: 0xxxxxxxxx (10 số) hoặc +84xxxxxxxxx
_PHONE = re.compile(r"(?:\+84|0)\d{9,10}\b")

_MASK = "[đã ẩn]"


def che_thong_tin_ca_nhan(text: str) -> tuple[str, bool]:
    """Che email/SĐT lộ trong text. Trả (text_đã_che, có_lộ_hay_không)."""
    found = bool(_EMAIL.search(text) or _PHONE.search(text))
    text = _EMAIL.sub(_MASK, text)
    text = _PHONE.sub(_MASK, text)
    return text, found
