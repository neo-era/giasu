import json

from pydantic import BaseModel

from app.config import settings
from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class TestResult(BaseModel):
    __test__ = False  # không phải test class của pytest

    output: str
    expected: str
    time_ms: int
    mem_kb: int


class JudgeResult(BaseModel):
    verdict: str
    chi_tiet: list[str] = []


def _verdict_test(t: TestResult, time_limit_ms: int, mem_limit_kb: int) -> str:
    if t.time_ms > time_limit_ms:
        return "TLE"
    if t.mem_kb > mem_limit_kb:
        return "MLE"
    if t.output.strip() != t.expected.strip():
        return "WA"
    return "AC"


def cham(
    test_results: list[TestResult], time_limit_ms: int = 1000, mem_limit_kb: int = 262144
) -> JudgeResult:
    """Chấm theo bộ test: AC nếu tất cả pass; nếu không, lấy verdict lỗi đầu tiên."""
    verdicts = [_verdict_test(t, time_limit_ms, mem_limit_kb) for t in test_results]
    tong = "AC" if all(v == "AC" for v in verdicts) else next(v for v in verdicts if v != "AC")
    return JudgeResult(verdict=tong, chi_tiet=verdicts)


def sandbox_san_sang() -> bool:
    """Sandbox chỉ mở khi đã bật (sau kiểm thử bảo mật) — FR-E07."""
    return settings.virtual_judge_enabled


def phan_tich(de: str, ma_nguon: str, ket_qua_judge: str, llm: LLMService | None = None) -> dict:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("virtual_judge").text
    payload = {"de": de, "ma_nguon": ma_nguon, "ket_qua_judge": ket_qua_judge}
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    return data if isinstance(data, dict) else {}
