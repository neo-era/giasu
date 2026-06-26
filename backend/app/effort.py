"""Cổng nỗ lực & tiết chế gợi ý (FR-L03/L04) — chống lệ thuộc.

Bảo mật học tập: quyết định mở lời giải đầy đủ dựa trên TRẠNG THÁI NỖ LỰC ở
backend (số lượt đã thử), KHÔNG dựa vào cách học sinh diễn đạt. Vì vậy không
thể "moi đáp án" bằng cách đổi câu chữ ("cho đáp án luôn", "bỏ qua gợi ý"…).
"""

from dataclasses import dataclass

from app.models.enums import CheDoTraLoi

NGUONG_NO_LUC = 2  # số lượt HS phải thử trước khi được mở lời giải đầy đủ
GIOI_HAN_GOI_Y = 5  # số gợi ý tối đa trước khi tiết chế


@dataclass
class TrangThaiNoLuc:
    so_luot_hs: int
    so_goi_y_da_dung: int


def da_qua_cong_no_luc(state: TrangThaiNoLuc, che_do: CheDoTraLoi) -> bool:
    """Chỉ mở lời giải đầy đủ khi HS yêu cầu RÕ và đã thử đủ số lượt."""
    return che_do == CheDoTraLoi.loi_giai_day_du and state.so_luot_hs >= NGUONG_NO_LUC


def con_duoc_goi_y(state: TrangThaiNoLuc) -> bool:
    return state.so_goi_y_da_dung < GIOI_HAN_GOI_Y


_TIET_CHE = (
    "LƯU Ý TIẾT CHẾ: em đã dùng nhiều gợi ý — hãy khuyến khích em tự làm lại từ "
    "đầu hoặc tạm nghỉ; HẠN CHẾ đưa thêm gợi ý mới."
)


def directive_tiet_che() -> str:
    return _TIET_CHE
