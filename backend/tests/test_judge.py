import pytest

from app.auth import otp
from app.judge.service import TestResult, cham

FIXED = "123456"


def _tr(output, expected, time_ms=10, mem_kb=1000):
    return TestResult(output=output, expected=expected, time_ms=time_ms, mem_kb=mem_kb)


def test_cham_ac():
    r = cham([_tr("5", "5"), _tr("10", "10")])
    assert r.verdict == "AC"


def test_cham_wa():
    assert cham([_tr("5", "6")]).verdict == "WA"


def test_cham_tle():
    assert cham([_tr("5", "5", time_ms=9999)], time_limit_ms=1000).verdict == "TLE"


def test_cham_mle():
    assert cham([_tr("5", "5", mem_kb=10**9)], mem_limit_kb=262144).verdict == "MLE"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email="elite@x.com"):
    client.post(
        "/auth/register",
        json={"email": email, "password": "matkhau123", "phan_khuc": "tinh_hoa"},
    )
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_sandbox_tat_mac_dinh_chan_run(client):
    h = _auth(client)
    # Cổng an toàn: chưa bật sandbox → /judge/run trả 503
    r = client.post("/judge/run", json={"ngon_ngu": "python", "ma_nguon": "print(1)"}, headers=h)
    assert r.status_code == 503
