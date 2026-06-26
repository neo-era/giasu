from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KhaiNiemOn, NguoiDung
from app.tat_ai.service import bang_tu_giai


def con_cua(db: Session, phu_huynh_id: str) -> list[NguoiDung]:
    return list(db.scalars(select(NguoiDung).where(NguoiDung.phu_huynh_id == phu_huynh_id)).all())


def la_con(db: Session, phu_huynh_id: str, child_id: str) -> bool:
    child = db.get(NguoiDung, child_id)
    return child is not None and child.phu_huynh_id == phu_huynh_id


def bao_cao_con(db: Session, child_id: str) -> dict:
    khai_niem = db.scalars(
        select(KhaiNiemOn)
        .where(KhaiNiemOn.nguoi_dung_id == child_id)
        .order_by(KhaiNiemOn.so_lan_sai.desc())
        .limit(5)
    ).all()
    child = db.get(NguoiDung, child_id)
    muc_do = child.ho_so.muc_do.value if (child and child.ho_so and child.ho_so.muc_do) else None
    return {
        "ty_le_tu_giai": bang_tu_giai(db, child_id),
        "khai_niem_hay_sai": [
            {"khai_niem": k.khai_niem, "so_lan_sai": k.so_lan_sai} for k in khai_niem
        ],
        "muc_do": muc_do,
    }
