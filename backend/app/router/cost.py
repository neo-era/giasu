from app.config import settings
from app.llm.tiers import BacModel


def uoc_tinh_chi_phi(bac: BacModel | str, token_vao: int, token_ra: int) -> float:
    """Ước tính chi phí (USD) cho một lượt gọi theo bậc model (FR-C11, NFR-41).

    Dùng bảng giá USD/1 triệu token trong cấu hình; chưa tính giảm giá cache.
    """
    key = bac.value if isinstance(bac, BacModel) else str(bac)
    gia = settings.llm_tier_price.get(key)
    if not gia:
        return 0.0
    gia_vao, gia_ra = gia[0], gia[1]
    return token_vao / 1_000_000 * gia_vao + token_ra / 1_000_000 * gia_ra
