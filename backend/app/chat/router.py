from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.chat.schemas import (
    ConversationCreate,
    ConversationOut,
    MessageIn,
    MessageOut,
)
from app.chat.service import (
    build_system_prompt,
    history_messages,
    luu_tin_nhan,
    make_routing_request,
    uoc_tinh_token_vao,
    user_context,
)
from app.db.session import get_db
from app.llm import ChatMessage, get_llm_service
from app.models import HoiThoai, NguoiDung, TinNhan
from app.models.enums import VaiTinNhan
from app.router import LLMRouter

router = APIRouter(prefix="/chat", tags=["chat"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


def _get_owned_conv(db: Session, conv_id: str, user: NguoiDung) -> HoiThoai:
    conv = db.get(HoiThoai, conv_id)
    if conv is None or conv.nguoi_dung_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy hội thoại")
    return conv


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(body: ConversationCreate, db: DbDep, user: UserDep) -> HoiThoai:
    phan_khuc, _, _ = user_context(db, user)
    conv = HoiThoai(
        nguoi_dung_id=user.id,
        phan_khuc=phan_khuc,
        chu_de=body.chu_de or "Cuộc trò chuyện",
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(db: DbDep, user: UserDep) -> list[HoiThoai]:
    return list(
        db.scalars(
            select(HoiThoai)
            .where(HoiThoai.nguoi_dung_id == user.id)
            .order_by(HoiThoai.updated_at.desc())
        ).all()
    )


@router.get("/conversations/{conv_id}/messages", response_model=list[MessageOut])
def list_messages(conv_id: str, db: DbDep, user: UserDep) -> list[TinNhan]:
    _get_owned_conv(db, conv_id, user)
    return list(
        db.scalars(
            select(TinNhan).where(TinNhan.hoi_thoai_id == conv_id).order_by(TinNhan.created_at)
        ).all()
    )


def _prepare(db: Session, conv: HoiThoai, user: NguoiDung, body: MessageIn):
    """Định tuyến + dựng messages. Trả (decision, model, messages)."""
    phan_khuc, is_free, level = user_context(db, user)
    decision = LLMRouter().route(
        make_routing_request(phan_khuc, is_free, body.do_kho, bool(body.anh_url))
    )
    system = build_system_prompt(decision.persona, level)
    messages = [ChatMessage(role="system", content=system)]
    messages += history_messages(db, conv.id)
    messages.append(ChatMessage(role="user", content=body.noi_dung))
    _, model = get_llm_service().resolve(decision.bac)
    return decision, model, messages


@router.post("/conversations/{conv_id}/messages", response_model=MessageOut)
def send_message(conv_id: str, body: MessageIn, db: DbDep, user: UserDep) -> TinNhan:
    conv = _get_owned_conv(db, conv_id, user)
    decision, _, messages = _prepare(db, conv, user, body)

    luu_tin_nhan(db, conv, vai=VaiTinNhan.nguoi_dung, noi_dung=body.noi_dung, anh_url=body.anh_url)
    result = get_llm_service().complete(decision.bac, messages)
    assistant = luu_tin_nhan(
        db,
        conv,
        vai=VaiTinNhan.tro_ly,
        noi_dung=result.text,
        model_dung=result.model,
        token_vao=result.token_in,
        token_ra=result.token_out,
    )
    db.commit()
    db.refresh(assistant)
    return assistant


@router.post("/conversations/{conv_id}/stream")
def stream_message(conv_id: str, body: MessageIn, db: DbDep, user: UserDep) -> StreamingResponse:
    conv = _get_owned_conv(db, conv_id, user)
    decision, model, messages = _prepare(db, conv, user, body)
    token_vao = uoc_tinh_token_vao(messages)

    luu_tin_nhan(db, conv, vai=VaiTinNhan.nguoi_dung, noi_dung=body.noi_dung, anh_url=body.anh_url)
    db.commit()

    def generate():
        parts: list[str] = []
        for chunk in get_llm_service().stream(decision.bac, messages):
            parts.append(chunk)
            yield f"data: {chunk}\n\n"
        full = "".join(parts)
        luu_tin_nhan(
            db,
            conv,
            vai=VaiTinNhan.tro_ly,
            noi_dung=full,
            model_dung=model,
            token_vao=token_vao,
            token_ra=len(full.split()),
        )
        db.commit()
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
