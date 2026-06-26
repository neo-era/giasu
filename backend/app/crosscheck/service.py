from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models import HangDoiDuyet, NguoiDung
from app.models.enums import TrangThaiDuyet
from app.personas import get_persona_loader


class ComparisonResult(BaseModel):
    dap_so_khop: bool = False
    diem_bat_dong: list[str] = []
    danh_gia: str = "bat_dong_can_ra_soat"
    khuyen_nghi: str = "chuyen_nguoi_duyet"

    @property
    def can_nguoi_duyet(self) -> bool:
        return self.khuyen_nghi == "chuyen_nguoi_duyet"


def so_sanh(loi_giai_a: str, loi_giai_b: str, llm: LLMService | None = None) -> ComparisonResult:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("cross_check").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=f"Lời giải A:\n{loi_giai_a}\n\nLời giải B:\n{loi_giai_b}"),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        # Không so khớp được → an toàn: chuyển người duyệt (không tự khẳng định)
        return ComparisonResult()
    return ComparisonResult(
        dap_so_khop=bool(data.get("dap_so_khop", False)),
        diem_bat_dong=list(data.get("diem_bat_dong", [])),
        danh_gia=str(data.get("danh_gia", "bat_dong_can_ra_soat")),
        khuyen_nghi=str(data.get("khuyen_nghi", "chuyen_nguoi_duyet")),
    )


def _hai_loi_giai(cau_hoi: str, svc: LLMService) -> tuple[str, str]:
    a = svc.complete(
        BacModel.reasoning,
        [ChatMessage(role="user", content=f"Giải bài sau (cách 1):\n{cau_hoi}")],
    ).text
    b = svc.complete(
        BacModel.reasoning,
        [ChatMessage(role="user", content=f"Giải bài sau (cách khác, độc lập):\n{cau_hoi}")],
    ).text
    return a, b


def chay_cross_check(
    db: Session, cau_hoi: str, llm: LLMService | None = None
) -> tuple[ComparisonResult, str | None]:
    """Trả (kết quả so khớp, id hàng đợi duyệt nếu cần). Bất đồng → tạo HITL."""
    svc = llm or get_llm_service()
    a, b = _hai_loi_giai(cau_hoi, svc)
    cmp = so_sanh(a, b, svc)
    review_id: str | None = None
    if cmp.can_nguoi_duyet:
        item = HangDoiDuyet(
            loai="cross_check",
            noi_dung=cau_hoi,
            chi_tiet={
                "loi_giai_a": a,
                "loi_giai_b": b,
                "diem_bat_dong": cmp.diem_bat_dong,
            },
            trang_thai=TrangThaiDuyet.cho_duyet,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        review_id = item.id
    return cmp, review_id


def hang_doi_cho_duyet(db: Session) -> list[HangDoiDuyet]:
    return list(
        db.scalars(
            select(HangDoiDuyet)
            .where(HangDoiDuyet.trang_thai == TrangThaiDuyet.cho_duyet)
            .order_by(HangDoiDuyet.created_at)
        ).all()
    )


def duyet(db: Session, nguoi: NguoiDung, item_id: str, ket_luan: str) -> HangDoiDuyet | None:
    """HITL: người duyệt đưa kết luận cuối (đổi/chốt)."""
    item = db.get(HangDoiDuyet, item_id)
    if item is None:
        return None
    item.trang_thai = TrangThaiDuyet.da_duyet
    item.ket_luan_nguoi = ket_luan
    item.nguoi_duyet_id = nguoi.id
    db.commit()
    db.refresh(item)
    return item
