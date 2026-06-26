import pytest

from app.auth import otp

FIXED = "123456"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email="hs@x.com"):
    client.post("/auth/register", json={"email": email, "password": "matkhau123"})
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_tao_hoi_thoai_va_gui_tin_nhan(client):
    h = _auth(client)
    cid = client.post("/chat/conversations", json={"chu_de": "Tích phân"}, headers=h).json()["id"]

    r = client.post(
        f"/chat/conversations/{cid}/messages",
        json={"noi_dung": "Tính tích phân 2x+1"},
        headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["vai"] == "tro_ly"
    assert body["model_dung"]  # model được ghi lại (FR-C11)
    assert body["token_ra"] > 0

    msgs = client.get(f"/chat/conversations/{cid}/messages", headers=h).json()
    assert len(msgs) == 2  # lịch sử: user + assistant
    assert msgs[0]["vai"] == "nguoi_dung"
    assert msgs[1]["vai"] == "tro_ly"


def test_stream_ghi_token(client):
    h = _auth(client)
    cid = client.post("/chat/conversations", json={}, headers=h).json()["id"]

    with client.stream(
        "POST",
        f"/chat/conversations/{cid}/stream",
        json={"noi_dung": "2+2 bằng mấy"},
        headers=h,
    ) as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
    assert "data:" in body
    assert "[DONE]" in body

    msgs = client.get(f"/chat/conversations/{cid}/messages", headers=h).json()
    assert any(m["vai"] == "tro_ly" and m["token_ra"] > 0 for m in msgs)


def test_khong_so_huu_thi_chan(client):
    h1 = _auth(client, "a@x.com")
    h2 = _auth(client, "b@x.com")
    cid = client.post("/chat/conversations", json={}, headers=h1).json()["id"]
    assert client.get(f"/chat/conversations/{cid}/messages", headers=h2).status_code == 404


def test_lich_su_tai_lai_dung_thu_tu(client):
    h = _auth(client)
    cid = client.post("/chat/conversations", json={}, headers=h).json()["id"]
    client.post(f"/chat/conversations/{cid}/messages", json={"noi_dung": "câu 1"}, headers=h)
    client.post(f"/chat/conversations/{cid}/messages", json={"noi_dung": "câu 2"}, headers=h)
    msgs = client.get(f"/chat/conversations/{cid}/messages", headers=h).json()
    assert len(msgs) == 4  # 2 lượt × (user + assistant)
    assert msgs[0]["noi_dung"] == "câu 1"
