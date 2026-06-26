from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import PhanKhuc, VaiTro


class RegisterIn(BaseModel):
    email: str | None = None
    so_dien_thoai: str | None = None
    password: str
    vai_tro: VaiTro = VaiTro.hoc_sinh
    la_vi_thanh_nien: bool = False
    # Hồ sơ học sinh (FR-C02) — tùy chọn khi đăng ký
    phan_khuc: PhanKhuc = PhanKhuc.dai_tra
    lop: int | None = None
    mon: str | None = None
    doi_tuyen: str | None = None

    @model_validator(mode="after")
    def co_it_nhat_mot_dinh_danh(self) -> "RegisterIn":
        if not self.email and not self.so_dien_thoai:
            raise ValueError("Cần email hoặc số điện thoại")
        return self

    @property
    def dinh_danh(self) -> str:
        return self.email or self.so_dien_thoai  # type: ignore[return-value]


class VerifyOtpIn(BaseModel):
    dinh_danh: str
    ma: str


class LoginIn(BaseModel):
    dinh_danh: str
    password: str


class ConsentIn(BaseModel):
    child_id: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str | None
    so_dien_thoai: str | None
    vai_tro: VaiTro
