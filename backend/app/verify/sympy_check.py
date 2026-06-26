"""Kiểm chứng Cấp 1 — phần TÍNH TOÁN bằng SymPy (FR-C08, FR-M03).

Trung thực phạm vi (FR-L08): mọi kết quả ở đây chỉ chứng nhận PHẦN TÍNH TOÁN
(pham_vi_da_kiem = tinh_toan). Nội dung khái niệm/lập luận KHÔNG được khẳng
định đúng — dùng `danh_dau_khai_niem` để gắn cờ và chuyển người duyệt.
"""

from dataclasses import dataclass, field
from typing import Any

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.models.enums import PhamViKiemChung, TrangThaiKiemChung

_TRANSFORM = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)
_SAMPLE_POINTS = [sp.Rational(1, 3), sp.Rational(7, 5), sp.Rational(11, 7), sp.Integer(2)]


@dataclass
class VerifyResult:
    trang_thai: TrangThaiKiemChung
    pham_vi_da_kiem: PhamViKiemChung
    do_tin_cay: float
    chi_tiet: dict[str, Any] = field(default_factory=dict)


def _parse(s: str) -> sp.Expr:
    return parse_expr(s, transformations=_TRANSFORM)


def _khong_du_can_cu(ly_do: str) -> VerifyResult:
    return VerifyResult(
        trang_thai=TrangThaiKiemChung.khong_du_can_cu,
        pham_vi_da_kiem=PhamViKiemChung.tinh_toan,
        do_tin_cay=0.0,
        chi_tiet={"ly_do": ly_do},
    )


def _bang(a: sp.Expr, b: sp.Expr) -> tuple[bool, float]:
    """So khớp hai biểu thức: ưu tiên symbolic, dự phòng lấy mẫu số."""
    diff = sp.simplify(a - b)
    if diff == 0:
        return True, 1.0
    if diff.is_number:
        try:
            return abs(complex(diff)) < 1e-9, 1.0
        except (TypeError, ValueError):
            return False, 0.5
    syms = sorted(diff.free_symbols, key=str)
    try:
        for i in range(len(_SAMPLE_POINTS)):
            subs = {s: _SAMPLE_POINTS[(i + j) % len(_SAMPLE_POINTS)] for j, s in enumerate(syms)}
            val = complex(diff.subs(subs))
            if abs(val) > 1e-6:
                return False, 1.0
        return True, 0.95
    except (TypeError, ValueError, ZeroDivisionError):
        return False, 0.5


def _ket(dung: bool, conf: float, chi_tiet: dict[str, Any]) -> VerifyResult:
    if dung:
        trang_thai = TrangThaiKiemChung.dung
    elif conf >= 0.9:
        trang_thai = TrangThaiKiemChung.sai
    else:
        trang_thai = TrangThaiKiemChung.nghi_van
    return VerifyResult(
        trang_thai=trang_thai,
        pham_vi_da_kiem=PhamViKiemChung.tinh_toan,
        do_tin_cay=conf,
        chi_tiet=chi_tiet,
    )


def kiem_bien_doi(lhs: str, rhs: str) -> VerifyResult:
    """Kiểm hai biểu thức có tương đương đại số không."""
    try:
        a, b = _parse(lhs), _parse(rhs)
    except (SyntaxError, TypeError, sp.SympifyError):
        return _khong_du_can_cu("không phân tích được biểu thức")
    dung, conf = _bang(a, b)
    return _ket(dung, conf, {"lhs": lhs, "rhs": rhs})


def kiem_nghiem(phuong_trinh: str, nghiem_tuyen_bo: list[str], bien: str = "x") -> VerifyResult:
    """Giải phương trình và so với tập nghiệm học sinh tuyên bố."""
    x = sp.Symbol(bien)
    try:
        if "=" in phuong_trinh:
            lhs, rhs = phuong_trinh.split("=", 1)
            expr = _parse(lhs) - _parse(rhs)
        else:
            expr = _parse(phuong_trinh)
        thuc_te = sp.solve(expr, x)
        tuyen_bo = [_parse(s) for s in nghiem_tuyen_bo]
    except (SyntaxError, TypeError, sp.SympifyError, NotImplementedError):
        return _khong_du_can_cu("không giải được phương trình")

    def _trong(tap: list[sp.Expr], phan_tu: sp.Expr) -> bool:
        return any(_bang(phan_tu, t)[0] for t in tap)

    thieu = [str(s) for s in thuc_te if not _trong(tuyen_bo, s)]
    thua = [str(s) for s in tuyen_bo if not _trong(thuc_te, s)]
    dung = not thieu and not thua
    chi_tiet = {
        "nghiem_thuc_te": [str(s) for s in thuc_te],
        "nghiem_tuyen_bo": nghiem_tuyen_bo,
        "thieu": thieu,
        "thua": thua,
    }
    return _ket(dung, 1.0, chi_tiet)


def kiem_dao_ham(bieu_thuc: str, dao_ham_tuyen_bo: str, bien: str = "x") -> VerifyResult:
    x = sp.Symbol(bien)
    try:
        dung_thuc = sp.diff(_parse(bieu_thuc), x)
        claimed = _parse(dao_ham_tuyen_bo)
    except (SyntaxError, TypeError, sp.SympifyError):
        return _khong_du_can_cu("không phân tích được biểu thức")
    dung, conf = _bang(dung_thuc, claimed)
    return _ket(dung, conf, {"dao_ham_dung": str(dung_thuc), "tuyen_bo": dao_ham_tuyen_bo})


def kiem_tich_phan(
    bieu_thuc: str,
    ket_qua_tuyen_bo: str,
    bien: str = "x",
    can_duoi: str | None = None,
    can_tren: str | None = None,
) -> VerifyResult:
    """Tích phân bất định (so qua đạo hàm, bỏ qua hằng số C) hoặc xác định."""
    x = sp.Symbol(bien)
    try:
        f = _parse(bieu_thuc)
        claimed = _parse(ket_qua_tuyen_bo)
        if can_duoi is not None and can_tren is not None:
            dung_thuc = sp.integrate(f, (x, _parse(can_duoi), _parse(can_tren)))
            dung, conf = _bang(dung_thuc, claimed)
            chi_tiet = {"tich_phan_xac_dinh": str(dung_thuc)}
        else:
            # Bất định: kiểm đạo hàm của kết quả = hàm dưới dấu tích phân
            dung, conf = _bang(sp.diff(claimed, x), f)
            chi_tiet = {"kiem": "d/dx(ket_qua) == ham_duoi_dau_tich_phan"}
    except (SyntaxError, TypeError, sp.SympifyError, ValueError):
        return _khong_du_can_cu("không tính được tích phân")
    return _ket(dung, conf, chi_tiet)


def kiem_gia_tri_so(bieu_thuc: str, gia_tri_tuyen_bo: float, sai_so: float = 1e-6) -> VerifyResult:
    """Kiểm kết quả số (vd thay số ra đáp số có đơn vị)."""
    try:
        val = complex(_parse(bieu_thuc).evalf())
    except (SyntaxError, TypeError, sp.SympifyError, ValueError):
        return _khong_du_can_cu("không tính được giá trị số")
    dung = abs(val - gia_tri_tuyen_bo) <= sai_so
    return _ket(dung, 1.0, {"gia_tri_dung": str(val), "tuyen_bo": gia_tri_tuyen_bo})


def danh_dau_khai_niem(ghi_chu: str = "") -> VerifyResult:
    """Nội dung khái niệm/lập luận CHƯA kiểm được → gắn cờ trung thực (FR-L08).

    KHÔNG khẳng định đúng; cần dẫn dắt + chuyển người duyệt.
    """
    return VerifyResult(
        trang_thai=TrangThaiKiemChung.khong_du_can_cu,
        pham_vi_da_kiem=PhamViKiemChung.khai_niem,
        do_tin_cay=0.0,
        chi_tiet={"ghi_chu": ghi_chu or "Nội dung khái niệm chưa kiểm chứng được"},
    )
