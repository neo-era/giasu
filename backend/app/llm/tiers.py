import enum


class BacModel(str, enum.Enum):
    """Bậc định tuyến theo chi phí/độ trễ — KHÔNG gán cứng thương hiệu (FR-C07)."""

    re = "re"
    can_bang = "can_bang"
    reasoning = "reasoning"
    vision = "vision"
