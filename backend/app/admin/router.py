from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.db.session import get_db
from app.llm.service import get_llm_service
from app.metrics.service import chi_phi_token
from app.models import NguoiDung
from app.models.enums import TrangThaiNguoiDung, VaiTro
from app.personas import get_persona_loader
from app.runtime_config import get_tiers, set_tiers

router = APIRouter(prefix="/admin", tags=["admin"])

DbDep = Annotated[Session, Depends(get_db)]
AdminDep = Annotated[NguoiDung, Depends(require_roles(VaiTro.quan_tri))]


class UserAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str | None
    vai_tro: VaiTro
    trang_thai: TrangThaiNguoiDung


class UserPatch(BaseModel):
    vai_tro: VaiTro | None = None
    trang_thai: TrangThaiNguoiDung | None = None


class RouterConfigIn(BaseModel):
    tiers: dict[str, str]


@router.get("/users", response_model=list[UserAdminOut])
def list_users(db: DbDep, _: AdminDep) -> list[NguoiDung]:
    return list(db.scalars(select(NguoiDung).order_by(NguoiDung.created_at.desc())).all())


@router.patch("/users/{user_id}", response_model=UserAdminOut)
def patch_user(user_id: str, body: UserPatch, db: DbDep, _: AdminDep) -> NguoiDung:
    u = db.get(NguoiDung, user_id)
    if u is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")
    if body.vai_tro is not None:
        u.vai_tro = body.vai_tro
    if body.trang_thai is not None:
        u.trang_thai = body.trang_thai
    db.commit()
    db.refresh(u)
    return u


@router.get("/config/router")
def get_router_config(_: AdminDep) -> dict[str, dict[str, str]]:
    return {"tiers": get_tiers()}


@router.put("/config/router")
def update_router_config(body: RouterConfigIn, _: AdminDep) -> dict[str, dict[str, str]]:
    # Áp dụng runtime — KHÔNG cần deploy lại (FR-C11).
    set_tiers(body.tiers)
    get_llm_service.cache_clear()
    return {"tiers": get_tiers()}


@router.post("/config/prompts/reload")
def reload_prompts(_: AdminDep) -> dict[str, str]:
    get_persona_loader().reload()
    return {"message": "Đã nạp lại prompt"}


@router.get("/cost")
def cost(db: DbDep, _: AdminDep) -> dict[str, list]:
    return {"chi_phi_token": chi_phi_token(db)}
