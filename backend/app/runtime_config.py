"""Cấu hình thay đổi lúc chạy (không cần deploy lại) — phục vụ trang quản trị.

Khởi tạo từ settings; quản trị có thể cập nhật ánh xạ bậc→model qua API.
"""

from app.config import settings

_tiers: dict[str, str] = dict(settings.llm_tiers)


def get_tiers() -> dict[str, str]:
    return dict(_tiers)


def set_tiers(tiers: dict[str, str]) -> None:
    global _tiers
    _tiers = dict(tiers)
