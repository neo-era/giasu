from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class DichResult(BaseModel):
    ban_dich: str = ""
    thuat_ngu: list[dict] = []
    cho_khong_chac: list[str] = []
    do_tin_cay: float = 0.0


def dich(noi_dung: str, llm: LLMService | None = None) -> DichResult:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("dich_thuat").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=noi_dung),
    ]
    try:
        out = svc.complete(BacModel.can_bang, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return DichResult(cho_khong_chac=["Không dịch tự động được — cần người rà"])
    return DichResult(
        ban_dich=str(data.get("ban_dich", "")),
        thuat_ngu=list(data.get("thuat_ngu", [])),
        cho_khong_chac=list(data.get("cho_khong_chac", [])),
        do_tin_cay=float(data.get("do_tin_cay", 0.0) or 0.0),
    )
