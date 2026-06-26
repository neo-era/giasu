from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import ChatMessage
from app.models import Goi, HoiThoai, NguoiDung, TinNhan
from app.models.enums import LoaiGoi, PhanKhuc, VaiTinNhan
from app.personas import get_persona_loader
from app.router import RoutingRequest


def user_context(db: Session, user: NguoiDung) -> tuple[PhanKhuc, bool, str]:
    """(phân khúc, là gói free, mức độ học) — đầu vào cho router & persona."""
    ho_so = user.ho_so
    phan_khuc = ho_so.phan_khuc if ho_so else PhanKhuc.dai_tra
    level = ho_so.muc_do.value if (ho_so and ho_so.muc_do) else "trung_binh"
    goi = db.scalar(select(Goi).where(Goi.nguoi_dung_id == user.id).order_by(Goi.created_at.desc()))
    is_free = goi is None or goi.loai == LoaiGoi.free
    return phan_khuc, is_free, level


def build_system_prompt(persona: str, level: str, chi_dan: str = "") -> str:
    loader = get_persona_loader()
    tpl = loader.load(persona)
    ctx = {"LEVEL": level}
    needed = {k: ctx.get(k, "") for k in tpl.required_vars}
    base = tpl.render(**needed)
    return f"{base}\n\n{chi_dan}" if chi_dan else base


def history_messages(db: Session, conv_id: str) -> list[ChatMessage]:
    rows = db.scalars(
        select(TinNhan).where(TinNhan.hoi_thoai_id == conv_id).order_by(TinNhan.created_at)
    ).all()
    out: list[ChatMessage] = []
    for m in rows:
        role = "user" if m.vai == VaiTinNhan.nguoi_dung else "assistant"
        out.append(ChatMessage(role=role, content=m.noi_dung))
    return out


def make_routing_request(
    phan_khuc: PhanKhuc, is_free: bool, body_do_kho, has_image: bool
) -> RoutingRequest:
    return RoutingRequest(
        phan_khuc=phan_khuc,
        do_kho=body_do_kho,
        is_free_plan=is_free,
        has_image=has_image,
    )


def luu_tin_nhan(
    db: Session,
    conv: HoiThoai,
    *,
    vai: VaiTinNhan,
    noi_dung: str,
    anh_url: str | None = None,
    model_dung: str | None = None,
    token_vao: int = 0,
    token_ra: int = 0,
) -> TinNhan:
    msg = TinNhan(
        hoi_thoai_id=conv.id,
        vai=vai,
        noi_dung=noi_dung,
        anh_url=anh_url,
        model_dung=model_dung,
        token_vao=token_vao,
        token_ra=token_ra,
    )
    db.add(msg)
    db.flush()
    return msg


def uoc_tinh_token_vao(messages: list[ChatMessage]) -> int:
    return sum(len(m.content.split()) for m in messages)
