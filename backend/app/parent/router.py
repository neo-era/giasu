from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.db.session import get_db
from app.models import NguoiDung
from app.models.enums import VaiTro
from app.parent.service import bao_cao_con, con_cua, la_con

router = APIRouter(prefix="/phu-huynh", tags=["phu-huynh"])

DbDep = Annotated[Session, Depends(get_db)]
ParentDep = Annotated[NguoiDung, Depends(require_roles(VaiTro.phu_huynh))]


@router.get("/con-cua-toi")
def con_cua_toi(db: DbDep, parent: ParentDep) -> list[dict]:
    return [{"id": c.id, "email": c.email} for c in con_cua(db, parent.id)]


@router.get("/con/{child_id}/bao-cao")
def bao_cao(child_id: str, db: DbDep, parent: ParentDep) -> dict:
    if not la_con(db, parent.id, child_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Không phải con của bạn")
    return bao_cao_con(db, child_id)
