from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader

# Các loại mục được tự đánh số
_DANH_SO = {"dinh_ly", "bo_de", "he_qua"}


class MucChuyenLuan(BaseModel):
    loai: str
    so: int = 0
    noi_dung_latex: str = ""


class ChuyenLuan(BaseModel):
    tieu_de: str = ""
    cau_truc: list[MucChuyenLuan] = []
    tom_tat: str = ""
    tai_lieu_tham_khao: list[str] = []


class ChuaDuyetError(Exception):
    """Nội dung chưa qua kiểm chứng + người duyệt — không được xuất."""


def _danh_so_lai(cau_truc: list[MucChuyenLuan]) -> list[MucChuyenLuan]:
    dem: dict[str, int] = {}
    for muc in cau_truc:
        if muc.loai in _DANH_SO:
            dem[muc.loai] = dem.get(muc.loai, 0) + 1
            muc.so = dem[muc.loai]
    return cau_truc


def bien_tap(noi_dung: str, da_duyet: bool, llm: LLMService | None = None) -> ChuyenLuan:
    if not da_duyet:
        raise ChuaDuyetError("Chỉ xuất chuyên luận từ nội dung đã kiểm chứng + duyệt")
    svc = llm or get_llm_service()
    system = get_persona_loader().load("chuyen_luan").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=noi_dung),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return ChuyenLuan()
    cau_truc = [
        MucChuyenLuan(
            loai=str(m.get("loai", "nhan_xet")),
            so=int(m.get("so", 0) or 0),
            noi_dung_latex=str(m.get("noi_dung_latex", "")),
        )
        for m in data.get("cau_truc", [])
    ]
    return ChuyenLuan(
        tieu_de=str(data.get("tieu_de", "")),
        cau_truc=_danh_so_lai(cau_truc),  # đánh số nhất quán phía server
        tom_tat=str(data.get("tom_tat", "")),
        tai_lieu_tham_khao=list(data.get("tai_lieu_tham_khao", [])),
    )
