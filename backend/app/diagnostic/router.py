from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.db.session import get_db
from app.diagnostic.schemas import DiagnosticIn, DiagnosticResult
from app.diagnostic.service import DiagnosticService
from app.models import NguoiDung
from app.models.enums import MucDoHoc

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


@router.post("/assess", response_model=DiagnosticResult)
def assess(body: DiagnosticIn, db: DbDep, user: UserDep) -> DiagnosticResult:
    result = DiagnosticService().assess(body)
    # Lưu mức độ vào hồ sơ để nuôi [LEVEL] cho persona (FR-L01 → FR-L02)
    if user.ho_so is not None:
        user.ho_so.muc_do = MucDoHoc(result.level)
        db.commit()
    return result
