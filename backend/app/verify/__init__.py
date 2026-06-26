"""Lớp kiểm chứng (FR-C08).

Cấp 1 — tính toán: `sympy_check.py` (B10). Cấp 2 — chứng minh (tinh hoa):
`crosscheck.py`, `rag.py` (B27/B28). Phạm vi "đã kiểm chứng" chỉ gồm phần
TÍNH TOÁN; nội dung khái niệm chưa kiểm phải gắn cờ độ tin cậy (FR-L08).
"""

from app.verify.service import can_nguoi_duyet, luu_ket_qua
from app.verify.sympy_check import (
    VerifyResult,
    danh_dau_khai_niem,
    kiem_bien_doi,
    kiem_dao_ham,
    kiem_gia_tri_so,
    kiem_nghiem,
    kiem_tich_phan,
)

__all__ = [
    "VerifyResult",
    "kiem_bien_doi",
    "kiem_nghiem",
    "kiem_dao_ham",
    "kiem_tich_phan",
    "kiem_gia_tri_so",
    "danh_dau_khai_niem",
    "luu_ket_qua",
    "can_nguoi_duyet",
]
