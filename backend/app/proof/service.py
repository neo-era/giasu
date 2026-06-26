from typing import Any

from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class BuocPhanBien(BaseModel):
    buoc: str
    trang_thai: str
    ly_do: str = ""


class CritiqueResult(BaseModel):
    cac_buoc: list[BuocPhanBien] = []
    edge_cases_bo_sot: list[str] = []
    ket_luan_so_bo: str = "khong_du_can_cu"
    do_tin_cay: float = 0.0
    can_nguoi_duyet: bool = True

    @property
    def phat_hien_lo_hong(self) -> bool:
        return self.ket_luan_so_bo == "co_lo_hong"


def critique(chung_minh: str, llm: LLMService | None = None) -> CritiqueResult:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("phan_bien").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=chung_minh),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        # Không phân tích được → trung thực: không đủ căn cứ, chuyển người duyệt
        return CritiqueResult()
    buoc = [
        BuocPhanBien(
            buoc=str(b.get("buoc", "")),
            trang_thai=str(b.get("trang_thai", "nghi_van")),
            ly_do=str(b.get("ly_do", "")),
        )
        for b in data.get("cac_buoc", [])
    ]
    return CritiqueResult(
        cac_buoc=buoc,
        edge_cases_bo_sot=list(data.get("edge_cases_bo_sot", [])),
        ket_luan_so_bo=str(data.get("ket_luan_so_bo", "khong_du_can_cu")),
        do_tin_cay=float(data.get("do_tin_cay", 0.0) or 0.0),
        can_nguoi_duyet=bool(data.get("can_nguoi_duyet", True)),
    )


def tinh_chi_so(ket_qua: list[tuple[bool, bool]]) -> dict[str, Any]:
    """Đo chất lượng phản biện. ket_qua: list (du_doan_co_loi, thuc_te_co_loi).

    detection_rate (recall): trong các CM thực sự có lỗi, bao nhiêu % bị phát hiện.
    false_positive_rate: trong các CM đúng, bao nhiêu % bị báo nhầm có lỗi.
    """
    tp = sum(1 for p, t in ket_qua if p and t)
    fp = sum(1 for p, t in ket_qua if p and not t)
    fn = sum(1 for p, t in ket_qua if not p and t)
    tn = sum(1 for p, t in ket_qua if not p and not t)
    co_loi = tp + fn
    khong_loi = fp + tn
    return {
        "tong": len(ket_qua),
        "detection_rate": (tp / co_loi) if co_loi else None,
        "false_positive_rate": (fp / khong_loi) if khong_loi else None,
        "false_negative_rate": (fn / co_loi) if co_loi else None,
    }
