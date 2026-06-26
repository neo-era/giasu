from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ChuDePhanAnh, TrangThaiKiemDuyet, TrangThaiPhanAnh


class FeedbackCreate(BaseModel):
    chu_de: ChuDePhanAnh
    tieu_de: str
    noi_dung: str
    anh_url: str | None = None
    an_danh: bool = False
    loi_giai_id: str | None = None


class FeedbackOut(BaseModel):
    id: str
    chu_de: ChuDePhanAnh
    tieu_de: str
    noi_dung: str
    anh_url: str | None
    trang_thai: TrangThaiPhanAnh
    trang_thai_kiem_duyet: TrangThaiKiemDuyet
    so_dong_tinh: int
    an_danh: bool
    nguoi_gui_id: str | None  # None khi ẩn danh
    created_at: datetime
