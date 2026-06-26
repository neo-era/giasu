import logging

from app.llm.tiers import BacModel
from app.models.enums import PhanKhuc
from app.router.policy import RoutingPolicy, default_policy
from app.router.schemas import (
    PERSONA_GIAO_SU_NGO,
    PERSONA_THAY_AN,
    RoutingDecision,
    RoutingRequest,
)

logger = logging.getLogger("giasu.router")


class LLMRouter:
    """Phân loại + định tuyến theo BẬC và phân khúc (FR-C07).

    KHÔNG gán cứng thương hiệu model — chỉ chọn bậc; bậc→model do `llm_tiers`.
    """

    def __init__(self, policy: RoutingPolicy | None = None) -> None:
        self.policy = policy or default_policy()

    def route(self, req: RoutingRequest) -> RoutingDecision:
        ly_do: list[str] = []

        can_ocr = req.has_image
        ocr_bac = BacModel.vision if can_ocr else None
        if can_ocr:
            ly_do.append("có ảnh → chạy OCR/phân loại (P3) ở bậc vision trước")

        if req.phan_khuc == PhanKhuc.tinh_hoa:
            bac = BacModel.reasoning
            persona = PERSONA_GIAO_SU_NGO
            ly_do.append("tinh hoa → bậc reasoning")
            cross = req.is_important or (req.do_kho in self.policy.crosscheck_levels)
            if cross:
                ly_do.append("bài quan trọng/độ khó cao → cross-check đa model")
            so_model = self.policy.crosscheck_models if cross else 0
        else:
            persona = PERSONA_THAY_AN
            cross = False
            so_model = 0
            if req.is_free_plan and self.policy.free_forces_cheap:
                bac = BacModel.re
                ly_do.append("gói free → bậc rẻ (bảo toàn biên — NFR-40)")
            elif req.do_kho in self.policy.simple_levels:
                bac = BacModel.re
                ly_do.append("câu đơn giản → bậc rẻ")
            else:
                bac = BacModel.can_bang
                ly_do.append("đại trà mặc định → bậc cân bằng")

        decision = RoutingDecision(
            bac=bac,
            persona=persona,
            can_ocr=can_ocr,
            ocr_bac=ocr_bac,
            cross_check=cross,
            so_model_cross_check=so_model,
            ly_do=ly_do,
        )
        logger.info(
            "route phan_khuc=%s bac=%s persona=%s ocr=%s cross=%s ly_do=%s",
            req.phan_khuc.value,
            decision.bac.value,
            decision.persona,
            decision.can_ocr,
            decision.cross_check,
            "; ".join(ly_do),
        )
        return decision
