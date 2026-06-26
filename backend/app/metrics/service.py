from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DoLuongHoc, HoiThoai, TinNhan
from app.models.enums import GiaiDoanDo, NhomThuNghiem


def ghi_do(
    db: Session,
    nguoi_dung_id: str,
    giai_doan: GiaiDoanDo,
    diem: float,
    *,
    tat_ai: bool = True,
    nhom: NhomThuNghiem = NhomThuNghiem.app,
) -> DoLuongHoc:
    rec = DoLuongHoc(
        nguoi_dung_id=nguoi_dung_id,
        giai_doan=giai_doan,
        diem=diem,
        tat_ai=tat_ai,
        nhom=nhom,
    )
    db.add(rec)
    db.flush()
    return rec


def _avg(db: Session, nhom: NhomThuNghiem, giai_doan: GiaiDoanDo) -> float | None:
    return db.scalar(
        select(func.avg(DoLuongHoc.diem)).where(
            DoLuongHoc.nhom == nhom,
            DoLuongHoc.giai_doan == giai_doan,
            DoLuongHoc.tat_ai.is_(True),
        )
    )


def learning_gain(db: Session) -> dict[str, Any]:
    """Learning gain = post - pre, theo từng nhóm (app vs đối chứng)."""
    out: dict[str, Any] = {}
    for nhom in NhomThuNghiem:
        pre = _avg(db, nhom, GiaiDoanDo.pre)
        post = _avg(db, nhom, GiaiDoanDo.post)
        gain = (post - pre) if (pre is not None and post is not None) else None
        out[nhom.value] = {
            "pre": float(pre) if pre is not None else None,
            "post": float(post) if post is not None else None,
            "gain": float(gain) if gain is not None else None,
        }
    return out


def ty_le_tu_giai(db: Session) -> float | None:
    """Điểm tự làm (tắt-AI) trung bình ở giai đoạn post, nhóm app (NFR-51)."""
    val = _avg(db, NhomThuNghiem.app, GiaiDoanDo.post)
    return float(val) if val is not None else None


def chi_phi_token(db: Session) -> list[dict[str, Any]]:
    """Tổng token theo phân khúc — driver chi phí (FR-C11)."""
    rows = db.execute(
        select(
            HoiThoai.phan_khuc,
            func.coalesce(func.sum(TinNhan.token_vao), 0),
            func.coalesce(func.sum(TinNhan.token_ra), 0),
            func.count(TinNhan.id),
        )
        .join(TinNhan, TinNhan.hoi_thoai_id == HoiThoai.id)
        .group_by(HoiThoai.phan_khuc)
    ).all()
    return [
        {
            "phan_khuc": pk.value,
            "token_vao": int(tv),
            "token_ra": int(tr),
            "so_tin_nhan": int(n),
        }
        for pk, tv, tr, n in rows
    ]


def dashboard(db: Session) -> dict[str, Any]:
    # CHỦ Ý: chỉ learning gain + chi phí. KHÔNG có chỉ số engagement.
    return {
        "learning_gain": learning_gain(db),
        "ty_le_tu_giai": ty_le_tu_giai(db),
        "chi_phi_token": chi_phi_token(db),
    }
