from dataclasses import dataclass, field

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models.enums import TrangThaiKiemDuyet
from app.personas import get_persona_loader

_MAP = {
    "cho_phep": TrangThaiKiemDuyet.cho_phep,
    "can_nguoi_duyet": TrangThaiKiemDuyet.can_nguoi_duyet,
    "chan": TrangThaiKiemDuyet.chan,
}


@dataclass
class ModerationResult:
    quyet_dinh: TrangThaiKiemDuyet
    vi_pham: list[str] = field(default_factory=list)
    co_lo_pii: bool = False


def classify_text(text: str, llm: LLMService | None = None) -> ModerationResult:
    """Phân loại nội dung bằng P9. Không phân tích được → cho_phep (PII vẫn được
    che riêng bằng regex tất định ở tầng gọi)."""
    svc = llm or get_llm_service()
    system = get_persona_loader().load("kiem_duyet").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=text),
    ]
    try:
        out = svc.complete(BacModel.re, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if data is None:
        return ModerationResult(quyet_dinh=TrangThaiKiemDuyet.cho_phep)
    quyet_dinh = _MAP.get(str(data.get("quyet_dinh")), TrangThaiKiemDuyet.cho_phep)
    return ModerationResult(
        quyet_dinh=quyet_dinh,
        vi_pham=list(data.get("vi_pham", [])),
        co_lo_pii=bool(data.get("co_lo_thong_tin_ca_nhan", False)),
    )
