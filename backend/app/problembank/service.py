import json

from sqlalchemy.orm import Session

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.models import DeBai, LoiGiai
from app.models.enums import CapDo, DoKho, PhamViKiemChung, TrangThaiKiemChung
from app.personas import get_persona_loader
from app.problembank.schemas import GenerateIn
from app.verify import kiem_nghiem, luu_ket_qua
from app.verify.sympy_check import VerifyResult

_DO_KHO = {d.value for d in DoKho}


def _do_kho(value: object) -> DoKho | None:
    return DoKho(value) if value in _DO_KHO else None


def _dap_an_str(dap_an: object) -> str:
    if isinstance(dap_an, list):
        return ", ".join(str(x) for x in dap_an)
    return "" if dap_an is None else str(dap_an)


def kiem_dap_an(de_latex: str, dap_an: object) -> VerifyResult:
    """Kiểm đáp án bằng SymPy khi đề là phương trình; nếu không tự kiểm được
    thì trả 'không đủ căn cứ' (cần người rà) — không khẳng định đúng."""
    expr = de_latex.strip().strip("$").strip()
    if "=" in expr and dap_an is not None:
        nghiem = dap_an if isinstance(dap_an, list) else [str(dap_an)]
        return kiem_nghiem(expr, [str(n) for n in nghiem])
    return VerifyResult(
        trang_thai=TrangThaiKiemChung.khong_du_can_cu,
        pham_vi_da_kiem=PhamViKiemChung.tinh_toan,
        do_tin_cay=0.0,
        chi_tiet={"ly_do": "đáp án không ở dạng tự kiểm được (cần người rà)"},
    )


class ProblemBankService:
    def __init__(self, db: Session, llm: LLMService | None = None) -> None:
        self.db = db
        self.llm = llm or get_llm_service()

    def generate(self, req: GenerateIn) -> list[tuple[DeBai, LoiGiai, VerifyResult]]:
        system = get_persona_loader().load("sinh_de").text
        payload = {
            "mon": req.mon,
            "lop": req.lop,
            "chuong": req.chuong,
            "do_kho": req.do_kho.value if req.do_kho else None,
            "so_luong": req.so_luong,
        }
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
        ]
        try:
            out = self.llm.complete(BacModel.can_bang, messages)
            data = extract_json(out.text)
        except LLMError:
            data = None
        items = data.get("cau_hoi", []) if isinstance(data, dict) else []

        ket_qua: list[tuple[DeBai, LoiGiai, VerifyResult]] = []
        for it in items:
            de_latex = str(it.get("de_latex", ""))
            de = DeBai(
                mon=req.mon,
                cap_do=CapDo.thpt,
                lop=req.lop,
                chuong=it.get("chuong") or req.chuong,
                do_kho=_do_kho(it.get("muc_do")) or req.do_kho,
                de_latex=de_latex,
            )
            self.db.add(de)
            self.db.flush()

            dap_an = it.get("dap_an_tham_khao")
            vr = kiem_dap_an(de_latex, dap_an)
            lg = LoiGiai(de_bai_id=de.id, dap_so=_dap_an_str(dap_an), la_mau=True)
            self.db.add(lg)
            self.db.flush()
            luu_ket_qua(self.db, vr, loi_giai_id=lg.id)
            ket_qua.append((de, lg, vr))

        self.db.commit()
        return ket_qua
