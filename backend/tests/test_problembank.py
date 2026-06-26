import json

import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.models.enums import TrangThaiKiemChung
from app.problembank.schemas import GenerateIn
from app.problembank.service import ProblemBankService, kiem_dap_an

FIXED = "123456"


def _items_json(items: list[dict]) -> str:
    return json.dumps({"cau_hoi": items}, ensure_ascii=False)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def _svc(session, items: list[dict]) -> ProblemBankService:
    registry.reset_registry()
    registry.register_provider(_Scripted(_items_json(items)))
    return ProblemBankService(session, LLMService(tiers={"can_bang": "scripted:m"}, backoff=0))


def test_kiem_dap_an_dung():
    vr = kiem_dap_an("$x^2 - 1 = 0$", ["1", "-1"])
    assert vr.trang_thai == TrangThaiKiemChung.dung


def test_kiem_dap_an_sai_bi_bat():
    vr = kiem_dap_an("$x^2 - 1 = 0$", ["1"])
    assert vr.trang_thai == TrangThaiKiemChung.sai


def test_generate_luu_de_va_kiem_dap_an(session):
    items = [
        {
            "de_latex": "$x^2 - 1 = 0$",
            "muc_do": "thong_hieu",
            "chuong": "Phương trình",
            "dap_an_tham_khao": ["1", "-1"],
        }
    ]
    svc = _svc(session, items)
    ket_qua = svc.generate(GenerateIn(mon="toan", lop=12, chuong="Phương trình"))
    registry.reset_registry()

    assert len(ket_qua) == 1
    de, lg, vr = ket_qua[0]
    assert de.chuong == "Phương trình"  # bám đúng chương
    assert lg.dap_so == "1, -1"
    assert vr.trang_thai == TrangThaiKiemChung.dung  # đáp án đã kiểm


# ---- API: HS không thấy đáp án ----


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email, vai_tro=None):
    body = {"email": email, "password": "matkhau123"}
    if vai_tro:
        body["vai_tro"] = vai_tro
    client.post("/auth/register", json=body)
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_hoc_sinh_khong_thay_dap_an(client):
    # HS thường không tạo được đề (RBAC)
    hs = _auth(client, "hs@x.com")
    assert client.post("/problems/generate", json={}, headers=hs).status_code == 403
    # Danh sách đề cho HS không chứa trường đáp án
    r = client.get("/problems", headers=hs)
    assert r.status_code == 200
    for de in r.json():
        assert "dap_so" not in de
