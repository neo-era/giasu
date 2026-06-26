from datetime import date, timedelta

from app.models import NguoiDung
from app.models.enums import TrangThaiNguoiDung, VaiTro
from app.spaced.service import chon_can_on, da_on, ghi_loi


def _user(session, email="hs@x.com") -> NguoiDung:
    u = NguoiDung(email=email, vai_tro=VaiTro.hoc_sinh, trang_thai=TrangThaiNguoiDung.hoat_dong)
    session.add(u)
    session.commit()
    return u


def test_uu_tien_hay_sai_va_lau_chua_on(session):
    u = _user(session)
    hom_nay = date(2026, 6, 27)
    # A: sai nhiều; B: sai ít; C: chưa tới hạn (tương lai)
    ghi_loi(session, u.id, "A", hom_nay)
    ghi_loi(session, u.id, "A", hom_nay)  # A sai 2 lần
    ghi_loi(session, u.id, "B", hom_nay)  # B sai 1 lần
    c = ghi_loi(session, u.id, "C", hom_nay)
    c.lan_on_ke_tiep = hom_nay + timedelta(days=5)  # C chưa tới hạn
    session.commit()

    items = chon_can_on(session, u.id, hom_nay)
    ten = [i.khai_niem for i in items]
    assert "C" not in ten  # chưa tới hạn → không chọn
    assert ten[0] == "A"  # hay sai nhất lên đầu
    assert set(ten) == {"A", "B"}


def test_da_on_day_lich_gian_cach(session):
    u = _user(session, "b@x.com")
    hom_nay = date(2026, 6, 27)
    item = ghi_loi(session, u.id, "X", hom_nay)
    assert item.lan_on_ke_tiep == hom_nay  # vừa sai → tới hạn ngay
    da_on(session, item, hom_nay)
    session.commit()
    # Sau khi ôn lần 1 → đẩy tới hạn ra 1 ngày (giãn cách)
    assert item.lan_on_ke_tiep == hom_nay + timedelta(days=1)
    assert chon_can_on(session, u.id, hom_nay) == []  # không còn tới hạn hôm nay
