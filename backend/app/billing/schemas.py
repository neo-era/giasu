from pydantic import BaseModel

from app.models.enums import LoaiGoi


class CheckoutIn(BaseModel):
    loai_goi: LoaiGoi


class CheckoutOut(BaseModel):
    ma_giao_dich: str
    so_tien: int
    vietqr: str


class WebhookIn(BaseModel):
    ma_giao_dich: str


class PlanOut(BaseModel):
    goi: LoaiGoi
    gioi_han_ngay: int | None
    da_dung_hom_nay: int
