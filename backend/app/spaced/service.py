import json
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models import KhaiNiemOn
from app.personas import get_persona_loader

# Lịch giãn cách (ngày) theo số lần ôn
_INTERVALS = [1, 3, 7, 16, 35]


def ghi_loi(
    db: Session, nguoi_dung_id: str, khai_niem: str, hom_nay: date | None = None
) -> KhaiNiemOn:
    hom_nay = hom_nay or date.today()
    item = db.scalar(
        select(KhaiNiemOn).where(
            KhaiNiemOn.nguoi_dung_id == nguoi_dung_id,
            KhaiNiemOn.khai_niem == khai_niem,
        )
    )
    if item is None:
        item = KhaiNiemOn(
            nguoi_dung_id=nguoi_dung_id,
            khai_niem=khai_niem,
            so_lan_sai=1,
            lan_on_ke_tiep=hom_nay,  # sai → cần ôn sớm
        )
        db.add(item)
    else:
        item.so_lan_sai += 1
        item.lan_on_ke_tiep = hom_nay  # sai lại → đẩy lên ôn sớm
    db.flush()
    return item


def da_on(db: Session, item: KhaiNiemOn, hom_nay: date | None = None) -> KhaiNiemOn:
    hom_nay = hom_nay or date.today()
    item.so_lan_on += 1
    khoang = _INTERVALS[min(item.so_lan_on - 1, len(_INTERVALS) - 1)]
    item.lan_on_ke_tiep = hom_nay + timedelta(days=khoang)
    db.flush()
    return item


def chon_can_on(
    db: Session, nguoi_dung_id: str, hom_nay: date | None = None, gioi_han: int = 5
) -> list[KhaiNiemOn]:
    """Khái niệm tới hạn ôn: ưu tiên hay sai + lâu chưa ôn (FR-L05)."""
    hom_nay = hom_nay or date.today()
    stmt = (
        select(KhaiNiemOn)
        .where(
            KhaiNiemOn.nguoi_dung_id == nguoi_dung_id,
            KhaiNiemOn.lan_on_ke_tiep <= hom_nay,
        )
        .order_by(KhaiNiemOn.so_lan_sai.desc(), KhaiNiemOn.lan_on_ke_tiep.asc())
        .limit(gioi_han)
    )
    return list(db.scalars(stmt).all())


def sinh_cau_on(khai_niem_list: list[str], llm: LLMService | None = None) -> list[dict]:
    if not khai_niem_list:
        return []
    svc = llm or get_llm_service()
    system = get_persona_loader().load("on_tap").text
    payload = {"khai_niem": khai_niem_list}
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
    ]
    try:
        out = svc.complete(BacModel.can_bang, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return []
    return list(data.get("cau_on_tap", []))
