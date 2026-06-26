from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class BuocCham(BaseModel):
    noi_dung: str
    dung: bool
    diem_thanh_phan: float
    nhan_xet: str = ""


class GradeResult(BaseModel):
    cac_buoc: list[BuocCham] = []
    tong_diem_uoc_luong: float = 0.0
    loi_pho_bien_mac_phai: list[str] = []
    goi_y_trinh_bay_de_an_diem: str = ""


def cham(
    bai_lam: str,
    loi_giai_mau: str,
    barem: str,
    diem_toi_da: float | None = None,
    llm: LLMService | None = None,
) -> GradeResult:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("cham_barem").text
    user = f"BÀI LÀM:\n{bai_lam}\n\nLỜI GIẢI MẪU:\n{loi_giai_mau}\n\nBAREM:\n{barem}"
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=user),
    ]
    try:
        out = svc.complete(BacModel.can_bang, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return GradeResult()

    buoc = [
        BuocCham(
            noi_dung=str(b.get("noi_dung", "")),
            dung=bool(b.get("dung", False)),
            diem_thanh_phan=float(b.get("diem_thanh_phan", 0) or 0),
            nhan_xet=str(b.get("nhan_xet", "")),
        )
        for b in data.get("cac_buoc", [])
    ]
    tong = float(data.get("tong_diem_uoc_luong", 0) or 0)
    # Không chấm khắt khe hơn barem: không vượt điểm tối đa nếu có
    if diem_toi_da is not None:
        tong = min(tong, diem_toi_da)
    return GradeResult(
        cac_buoc=buoc,
        tong_diem_uoc_luong=tong,
        loi_pho_bien_mac_phai=list(data.get("loi_pho_bien_mac_phai", [])),
        goi_y_trinh_bay_de_an_diem=str(data.get("goi_y_trinh_bay_de_an_diem", "")),
    )
