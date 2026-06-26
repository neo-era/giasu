"""Scaffolding thích ứng theo trình độ + tiến bộ (FR-L02).

Hiệu ứng đảo chiều chuyên môn: HS yếu cần giải mẫu rồi mờ dần (fading) tới gợi
ý thuần khi tiến bộ; HS giỏi học tốt hơn khi tự giải → KHÔNG ép giải mẫu.
"""

import enum

from app.models.enums import MucDoHoc


class MucHoTro(str, enum.Enum):
    socratic = "socratic"  # chỉ hỏi dẫn dắt
    goi_y_tung_buoc = "goi_y_tung_buoc"
    giai_mau = "giai_mau"  # cho ví dụ giải mẫu


_FROM_INDEX = {0: MucHoTro.socratic, 1: MucHoTro.goi_y_tung_buoc, 2: MucHoTro.giai_mau}
_BASE = {MucDoHoc.kha_gioi: 0, MucDoHoc.trung_binh: 1, MucDoHoc.yeu: 2}

_DIRECTIVE = {
    MucHoTro.giai_mau: (
        "MỨC HỖ TRỢ: cho MỘT ví dụ giải mẫu tương tự, rồi để em tự làm bài chính; " "gợi ý cụ thể."
    ),
    MucHoTro.goi_y_tung_buoc: "MỨC HỖ TRỢ: gợi ý từng bước, mờ dần khi em tiến bộ.",
    MucHoTro.socratic: "MỨC HỖ TRỢ: chỉ hỏi dẫn dắt kiểu Socratic, để em tự đi.",
}


def tinh_muc_ho_tro(
    level: MucDoHoc,
    so_dung_lien_tiep: int = 0,
    so_sai_lien_tiep: int = 0,
) -> MucHoTro:
    """Mức hỗ trợ = nền theo trình độ, mờ dần khi đúng liên tiếp, tăng khi sai."""
    base = _BASE.get(level, 1)
    idx = base - so_dung_lien_tiep // 3 + so_sai_lien_tiep // 2
    # HS giỏi KHÔNG bị ép giải mẫu (trần = goi_y_tung_buoc)
    tran = 1 if level == MucDoHoc.kha_gioi else 2
    idx = max(0, min(idx, tran))
    return _FROM_INDEX[idx]


def directive_ho_tro(muc: MucHoTro) -> str:
    return _DIRECTIVE[muc]
