from pydantic import BaseModel

from app.models.enums import MucDoHoc


class DiagnosticAnswer(BaseModel):
    cau_hoi: str
    dap_an_hs: str
    dung: bool
    thoi_gian_giay: int | None = None


class DiagnosticIn(BaseModel):
    mon: str = "toan"
    lop: int | None = None
    chuong: str | None = None
    ket_qua: list[DiagnosticAnswer]


class DiagnosticResult(BaseModel):
    level: MucDoHoc
    diem_manh: list[str] = []
    diem_yeu: list[str] = []
    khai_niem_can_on_truoc: list[str] = []
    do_tin_cay: float = 0.0
    ghi_chu_cho_giao_vien: str = ""
