from pydantic import BaseModel, ConfigDict

from app.models.enums import CapDo, DoKho


class GenerateIn(BaseModel):
    mon: str = "toan"
    lop: int | None = None
    chuong: str | None = None
    do_kho: DoKho | None = None
    so_luong: int = 3


class ProblemStudentOut(BaseModel):
    """Đề hiển thị cho học sinh — KHÔNG kèm đáp án (ẩn cho tới khi nỗ lực)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    mon: str
    cap_do: CapDo
    lop: int | None
    chuong: str | None
    do_kho: DoKho | None
    de_latex: str


class GeneratedProblemOut(BaseModel):
    """Kết quả sinh đề cho biên tập — kèm đáp án + trạng thái kiểm chứng."""

    id: str
    de_latex: str
    chuong: str | None
    do_kho: DoKho | None
    dap_so: str | None
    kiem_trang_thai: str
    can_nguoi_duyet: bool
