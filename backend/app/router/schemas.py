from dataclasses import dataclass, field

from app.llm.tiers import BacModel
from app.models.enums import DoKho, PhanKhuc

# Tên persona nạp từ /prompts (FR-C07 → persona loader B06)
PERSONA_THAY_AN = "thay_an"  # P1 — đại trà
PERSONA_GIAO_SU_NGO = "giao_su_ngo"  # P2 — tinh hoa


@dataclass
class RoutingRequest:
    phan_khuc: PhanKhuc
    has_image: bool = False
    do_kho: DoKho | None = None
    is_free_plan: bool = False
    is_important: bool = False  # bài quan trọng → cross-check (tinh hoa)
    intent: str = "hoi_bai"


@dataclass
class RoutingDecision:
    bac: BacModel
    persona: str
    can_ocr: bool
    ocr_bac: BacModel | None
    cross_check: bool
    so_model_cross_check: int
    ly_do: list[str] = field(default_factory=list)
