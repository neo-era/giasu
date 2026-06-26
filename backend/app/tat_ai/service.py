import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models import DoLuongHoc
from app.models.enums import GiaiDoanDo
from app.personas import get_persona_loader


def sinh_de(khai_niem_list: list[str], llm: LLMService | None = None) -> dict:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("kiem_tra_tat_ai").text
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
        return {"muc_tieu_do": [], "cau_hoi": [], "huong_dan_lam_bai": ""}
    return data


def hieu_chinh_do_kho(diem: float, thang_diem: float = 10.0) -> str:
    """Giữ HS trong 'vùng vật lộn hiệu quả' (FR-L09)."""
    ti_le = diem / thang_diem if thang_diem else 0.0
    if ti_le >= 0.8:
        return "tang"  # quá dễ → tăng độ khó
    if ti_le <= 0.4:
        return "giam"  # quá khó → giảm độ khó
    return "giu"


def bang_tu_giai(db: Session, nguoi_dung_id: str) -> list[float]:
    """Dãy điểm tự làm (tắt-AI) theo thời gian — tỷ lệ tự giải (FR-L07)."""
    rows = db.scalars(
        select(DoLuongHoc)
        .where(
            DoLuongHoc.nguoi_dung_id == nguoi_dung_id,
            DoLuongHoc.giai_doan == GiaiDoanDo.post,
            DoLuongHoc.tat_ai.is_(True),
        )
        .order_by(DoLuongHoc.created_at)
    ).all()
    return [r.diem for r in rows]
