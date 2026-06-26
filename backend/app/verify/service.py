from sqlalchemy.orm import Session

from app.models import KetQuaKiemChung
from app.models.enums import PhamViKiemChung, PhuongPhapKiemChung, TrangThaiKiemChung
from app.verify.sympy_check import VerifyResult


def can_nguoi_duyet(result: VerifyResult) -> bool:
    """Cần người duyệt khi chưa chắc, không đủ căn cứ, hoặc là nội dung khái niệm."""
    return result.pham_vi_da_kiem == PhamViKiemChung.khai_niem or result.trang_thai in (
        TrangThaiKiemChung.nghi_van,
        TrangThaiKiemChung.khong_du_can_cu,
    )


def luu_ket_qua(
    db: Session,
    result: VerifyResult,
    *,
    tin_nhan_id: str | None = None,
    loi_giai_id: str | None = None,
    phuong_phap: PhuongPhapKiemChung = PhuongPhapKiemChung.sympy,
) -> KetQuaKiemChung:
    kq = KetQuaKiemChung(
        tin_nhan_id=tin_nhan_id,
        loi_giai_id=loi_giai_id,
        phuong_phap=phuong_phap,
        trang_thai=result.trang_thai,
        pham_vi_da_kiem=result.pham_vi_da_kiem,
        do_tin_cay=result.do_tin_cay,
        can_nguoi_duyet=can_nguoi_duyet(result),
        chi_tiet=result.chi_tiet,
    )
    db.add(kq)
    db.flush()
    return kq
