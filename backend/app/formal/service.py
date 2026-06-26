from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class FormalResult(BaseModel):
    hinh_thuc_hoa_duoc: bool = False
    ly_do_neu_khong: str = ""
    phat_bieu_hinh_thuc: str = ""
    phac_thao_chien_luoc: list[str] = []
    gia_thiet_can_lam_ro: list[str] = []
    can_chuyen_chuyen_gia: bool = True


def hinh_thuc_hoa(menh_de: str, llm: LLMService | None = None) -> FormalResult:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("lean_coq").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=menh_de),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        # Không phân tích được → không hình thức hóa, chuyển chuyên gia (không tự nhận đúng)
        return FormalResult(
            ly_do_neu_khong="Không phân tích được mệnh đề", can_chuyen_chuyen_gia=True
        )
    return FormalResult(
        hinh_thuc_hoa_duoc=bool(data.get("hinh_thuc_hoa_duoc", False)),
        ly_do_neu_khong=str(data.get("ly_do_neu_khong", "")),
        phat_bieu_hinh_thuc=str(data.get("phat_bieu_hinh_thuc", "")),
        phac_thao_chien_luoc=list(data.get("phac_thao_chien_luoc", [])),
        gia_thiet_can_lam_ro=list(data.get("gia_thiet_can_lam_ro", [])),
        can_chuyen_chuyen_gia=bool(data.get("can_chuyen_chuyen_gia", True)),
    )
