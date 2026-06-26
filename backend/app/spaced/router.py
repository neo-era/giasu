from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.db.session import get_db
from app.models import NguoiDung
from app.spaced.service import chon_can_on, ghi_loi, sinh_cau_on

router = APIRouter(prefix="/on-tap", tags=["on-tap"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


class GhiLoiIn(BaseModel):
    khai_niem: str


@router.post("/ghi-loi", status_code=201)
def ghi_loi_endpoint(body: GhiLoiIn, db: DbDep, user: UserDep) -> dict[str, str]:
    item = ghi_loi(db, user.id, body.khai_niem)
    db.commit()
    return {"id": item.id}


@router.get("/can-on")
def can_on(db: DbDep, user: UserDep) -> dict:
    items = chon_can_on(db, user.id)
    khai_niem = [i.khai_niem for i in items]
    return {"khai_niem": khai_niem, "cau_on_tap": sinh_cau_on(khai_niem)}
