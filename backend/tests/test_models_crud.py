from sqlalchemy import select

from app.models import (
    BinhLuan,
    DeBai,
    HoSoHocSinh,
    KetQuaKiemChung,
    LoiGiai,
    NguoiDung,
    PhanAnh,
)
from app.models.enums import (
    ChuDePhanAnh,
    PhamViKiemChung,
    PhanKhuc,
    PhuongPhapKiemChung,
    TrangThaiKiemChung,
    TrangThaiKiemDuyet,
    TrangThaiNguoiDung,
    TrangThaiPhanAnh,
    VaiTro,
)


def test_tao_nguoi_dung_va_ho_so(session):
    user = NguoiDung(
        email="hs@example.com",
        vai_tro=VaiTro.hoc_sinh,
        trang_thai=TrangThaiNguoiDung.hoat_dong,
        la_vi_thanh_nien=True,
        dong_y_phu_huynh=True,
    )
    user.ho_so = HoSoHocSinh(phan_khuc=PhanKhuc.dai_tra, lop=12, mon="toan")
    session.add(user)
    session.commit()

    got = session.scalar(select(NguoiDung).where(NguoiDung.email == "hs@example.com"))
    assert got is not None
    assert got.id  # id tự sinh
    assert got.ho_so.lop == 12
    assert got.ho_so.phan_khuc == PhanKhuc.dai_tra
    assert got.created_at is not None


def test_default_phan_anh_va_phan_hoi_chinh_thuc(session):
    pa = PhanAnh(
        chu_de=ChuDePhanAnh.loi_loi_giai,
        tieu_de="Lời giải bài tích phân sai",
        noi_dung="Bước 2 hình như nhầm dấu.",
        an_danh=True,
    )
    session.add(pa)
    session.commit()

    # Mặc định: trạng thái 'moi', kiểm duyệt 'cho_duyet' (FR-F06, FR-F08)
    assert pa.trang_thai == TrangThaiPhanAnh.moi
    assert pa.trang_thai_kiem_duyet == TrangThaiKiemDuyet.cho_duyet
    assert pa.so_dong_tinh == 0

    reply = BinhLuan(
        phan_anh_id=pa.id,
        vai_tro_nguoi_dang=VaiTro.bien_tap,
        la_phan_hoi_chinh_thuc=True,
        noi_dung="Cảm ơn bạn, đội ngũ đã ghi nhận và sẽ sửa.",
    )
    session.add(reply)
    session.commit()

    assert len(pa.binh_luan) == 1
    assert pa.binh_luan[0].la_phan_hoi_chinh_thuc is True


def test_loi_giai_va_ket_qua_kiem_chung(session):
    de = DeBai(mon="toan", de_latex=r"Giải $x^2-1=0$.")
    de.loi_giai = [LoiGiai(cac_buoc=[{"buoc": "x^2=1"}, {"buoc": "x=±1"}], dap_so="x=±1")]
    session.add(de)
    session.commit()

    lg = de.loi_giai[0]
    kq = KetQuaKiemChung(
        loi_giai_id=lg.id,
        phuong_phap=PhuongPhapKiemChung.sympy,
        trang_thai=TrangThaiKiemChung.dung,
        pham_vi_da_kiem=PhamViKiemChung.tinh_toan,
        do_tin_cay=1.0,
    )
    session.add(kq)
    session.commit()

    got = session.get(KetQuaKiemChung, kq.id)
    assert got.trang_thai == TrangThaiKiemChung.dung
    # Trung thực phạm vi: chỉ kiểm phần tính toán (FR-L08)
    assert got.pham_vi_da_kiem == PhamViKiemChung.tinh_toan
    assert lg.cac_buoc[1]["buoc"] == "x=±1"
