import json

from app.diagnostic.schemas import DiagnosticIn, DiagnosticResult
from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models.enums import MucDoHoc
from app.personas import get_persona_loader

_LEVELS = {m.value for m in MucDoHoc}


def _level(value: object) -> MucDoHoc:
    return MucDoHoc(value) if value in _LEVELS else MucDoHoc.trung_binh


class DiagnosticService:
    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or get_llm_service()

    def assess(self, data: DiagnosticIn) -> DiagnosticResult:
        system = get_persona_loader().load("chan_doan").text
        payload = {
            "mon": data.mon,
            "lop": data.lop,
            "chuong": data.chuong,
            "ket_qua": [a.model_dump() for a in data.ket_qua],
        }
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
        ]
        try:
            out = self.llm.complete(BacModel.can_bang, messages)
            parsed = extract_json(out.text)
        except LLMError:
            parsed = None

        if parsed is None:
            # Không phân loại được → mặc định trung bình, tin cậy 0 (cần người rà)
            return DiagnosticResult(
                level=MucDoHoc.trung_binh,
                do_tin_cay=0.0,
                ghi_chu_cho_giao_vien="Chưa phân loại tự động được — cần giáo viên rà.",
            )
        return DiagnosticResult(
            level=_level(parsed.get("level")),
            diem_manh=list(parsed.get("diem_manh", [])),
            diem_yeu=list(parsed.get("diem_yeu", [])),
            khai_niem_can_on_truoc=list(parsed.get("khai_niem_can_on_truoc", [])),
            do_tin_cay=float(parsed.get("do_tin_cay", 0.0) or 0.0),
            ghi_chu_cho_giao_vien=str(parsed.get("ghi_chu_cho_giao_vien", "")),
        )
