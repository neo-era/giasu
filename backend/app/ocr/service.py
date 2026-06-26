import json

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.service import LLMService, get_llm_service
from app.ocr.schemas import OcrResult
from app.personas import get_persona_loader


def _extract_json(text: str) -> dict | None:
    """Lấy object JSON đầu tiên trong text (model có thể kèm chữ thừa)."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


class OcrService:
    """Số hóa đề bằng P3 (bậc vision). Áp ngưỡng tin cậy để buộc xác nhận."""

    def __init__(self, llm: LLMService | None = None, threshold: float = 0.6) -> None:
        self.llm = llm or get_llm_service()
        self.threshold = threshold

    def _fallback(self, text: str | None) -> OcrResult:
        # Không đọc được → an toàn: yêu cầu xác nhận (chống sai dây chuyền)
        return OcrResult(
            de_latex=text or "",
            mon="khac",
            lop=None,
            phan_khuc_goi_y="dai_tra",
            do_kho=None,
            ocr_tin_cay=0.0,
            can_xac_nhan_lai=True,
        )

    def extract(self, *, image: str | None = None, text: str | None = None) -> OcrResult:
        system = get_persona_loader().load("ocr").text
        user = text or "(đề ở ảnh đính kèm)"
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user, images=[image] if image else None),
        ]
        try:
            result = self.llm.complete(BacModel.vision, messages)
        except LLMError:
            return self._fallback(text)

        data = _extract_json(result.text)
        if data is None:
            return self._fallback(text)

        try:
            tin_cay = float(data.get("ocr_tin_cay", 0.0))
        except (TypeError, ValueError):
            tin_cay = 0.0
        # Server-side: ảnh mờ (tin cậy thấp) LUÔN buộc xác nhận, dù model quên cờ
        can_xac_nhan = bool(data.get("can_xac_nhan_lai", False)) or tin_cay < self.threshold

        return OcrResult(
            de_latex=str(data.get("de_latex", "")),
            mon=str(data.get("mon", "khac")),
            lop=data.get("lop"),
            phan_khuc_goi_y=str(data.get("phan_khuc_goi_y", "dai_tra")),
            do_kho=data.get("do_kho"),
            ocr_tin_cay=tin_cay,
            can_xac_nhan_lai=can_xac_nhan,
        )
