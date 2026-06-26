from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import CapDo, DoKho


class OcrExtractIn(BaseModel):
    image: str | None = None  # URL hoặc data URI base64
    text: str | None = None

    @model_validator(mode="after")
    def co_dau_vao(self) -> "OcrExtractIn":
        if not self.image and not self.text:
            raise ValueError("Cần 'image' hoặc 'text'")
        return self


class OcrResult(BaseModel):
    de_latex: str
    mon: str
    lop: int | None
    phan_khuc_goi_y: str
    do_kho: str | None
    ocr_tin_cay: float
    can_xac_nhan_lai: bool


class OcrConfirmIn(BaseModel):
    de_latex: str
    mon: str = "toan"
    cap_do: CapDo = CapDo.thpt
    lop: int | None = None
    do_kho: DoKho | None = None
    # Cờ do tuyến đầu trả về + xác nhận của người dùng (chống sai dây chuyền)
    can_xac_nhan_lai: bool = False
    da_xac_nhan: bool = False


class DeBaiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mon: str
    cap_do: CapDo
    lop: int | None
    do_kho: DoKho | None
    de_latex: str
