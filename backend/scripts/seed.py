"""Seed tối thiểu: tài khoản quản trị + gói free + 1 đề mẫu.

Chạy sau khi `alembic upgrade head`:
    python scripts/seed.py

Idempotent: chạy lại không tạo trùng. Mật khẩu admin được đặt ở B03 (auth);
ở đây chỉ tạo bản ghi để hệ thống có 1 quản trị viên khởi đầu.
"""

import sys

from app.db.session import SessionLocal
from app.models import DeBai, Goi, NguoiDung
from app.models.enums import CapDo, DoKho, LoaiGoi, TrangThaiNguoiDung, VaiTro

ADMIN_EMAIL = "admin@giasu.local"


def run() -> None:
    # Tránh lỗi cp1252 khi in tiếng Việt trên console Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    with SessionLocal() as s:
        admin = s.query(NguoiDung).filter_by(email=ADMIN_EMAIL).first()
        if admin is None:
            admin = NguoiDung(
                email=ADMIN_EMAIL,
                vai_tro=VaiTro.quan_tri,
                trang_thai=TrangThaiNguoiDung.hoat_dong,
            )
            s.add(admin)
            s.flush()
            s.add(Goi(nguoi_dung_id=admin.id, loai=LoaiGoi.free))
            print(f"  + Tạo quản trị {ADMIN_EMAIL} + gói free")
        else:
            print("  = Quản trị đã tồn tại, bỏ qua")

        if s.query(DeBai).count() == 0:
            s.add(
                DeBai(
                    mon="toan",
                    cap_do=CapDo.thpt,
                    lop=12,
                    chuong="Nguyên hàm - Tích phân",
                    do_kho=DoKho.thong_hieu,
                    de_latex=r"Tính $\int_0^1 (2x+1)\,dx$.",
                )
            )
            print("  + Tạo 1 đề mẫu")
        else:
            print("  = Đã có đề, bỏ qua")

        s.commit()
    print("Seed xong.")


if __name__ == "__main__":
    run()
