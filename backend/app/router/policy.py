from dataclasses import dataclass, field

from app.config import settings
from app.models.enums import DoKho

# Mức độ "đơn giản" của đại trà → định tuyến bậc rẻ
SIMPLE_LEVELS = frozenset({DoKho.nhan_biet, DoKho.thong_hieu})
# Mức cần cross-check ở tinh hoa
CROSSCHECK_LEVELS = frozenset({DoKho.van_dung_cao})


@dataclass
class RoutingPolicy:
    """Ngưỡng định tuyến — đổi qua đây/để override bằng config (FR-C07)."""

    simple_levels: frozenset[DoKho] = field(default_factory=lambda: SIMPLE_LEVELS)
    crosscheck_levels: frozenset[DoKho] = field(default_factory=lambda: CROSSCHECK_LEVELS)
    free_forces_cheap: bool = True
    crosscheck_models: int = 2


def default_policy() -> RoutingPolicy:
    return RoutingPolicy(crosscheck_models=settings.llm_crosscheck_models)
