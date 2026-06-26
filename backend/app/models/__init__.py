"""Mô hình dữ liệu (SRS §7). Import ở đây để đăng ký toàn bộ bảng vào
`Base.metadata` (phục vụ Alembic autogenerate và `create_all` trong test)."""

from app.db.base import Base
from app.models.auth import MaXacThuc
from app.models.billing import Goi, HanMuc, ThanhToan
from app.models.conversation import HoiThoai, TinNhan
from app.models.feedback import BinhLuan, PhanAnh
from app.models.metrics import DoLuongHoc
from app.models.problem import DeBai, LoiGiai
from app.models.user import HoSoHocSinh, NguoiDung
from app.models.verification import KetQuaKiemChung

__all__ = [
    "Base",
    "NguoiDung",
    "HoSoHocSinh",
    "HoiThoai",
    "TinNhan",
    "DeBai",
    "LoiGiai",
    "KetQuaKiemChung",
    "Goi",
    "HanMuc",
    "ThanhToan",
    "PhanAnh",
    "BinhLuan",
    "MaXacThuc",
    "DoLuongHoc",
]
