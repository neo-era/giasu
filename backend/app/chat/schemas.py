from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CheDoTraLoi, DoKho, PhanKhuc, VaiTinNhan


class ConversationCreate(BaseModel):
    chu_de: str | None = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chu_de: str | None
    phan_khuc: PhanKhuc
    created_at: datetime


class MessageIn(BaseModel):
    noi_dung: str
    do_kho: DoKho | None = None
    anh_url: str | None = None
    che_do: CheDoTraLoi = CheDoTraLoi.goi_y
    huong_tiep_can: str | None = None  # hướng HS chọn từ Strategy Tree (FR-E02)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vai: VaiTinNhan
    noi_dung: str
    anh_url: str | None
    model_dung: str | None
    token_vao: int
    token_ra: int
    created_at: datetime
