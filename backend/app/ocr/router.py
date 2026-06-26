from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.db.session import get_db
from app.models import DeBai, NguoiDung
from app.ocr.schemas import DeBaiOut, OcrConfirmIn, OcrExtractIn, OcrResult
from app.ocr.service import OcrService

router = APIRouter(prefix="/ocr", tags=["ocr"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


@router.post("/extract", response_model=OcrResult)
def extract(body: OcrExtractIn, _: UserDep) -> OcrResult:
    return OcrService().extract(image=body.image, text=body.text)


@router.post("/confirm", response_model=DeBaiOut, status_code=201)
def confirm(body: OcrConfirmIn, db: DbDep, _: UserDep) -> DeBai:
    # Chống sai dây chuyền: chưa xác nhận mà đề cần xác nhận → chặn (FR-C05)
    if body.can_xac_nhan_lai and not body.da_xac_nhan:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Đề cần được xác nhận/sửa trước khi xử lý",
        )
    de = DeBai(
        mon=body.mon,
        cap_do=body.cap_do,
        lop=body.lop,
        do_kho=body.do_kho,
        de_latex=body.de_latex,
    )
    db.add(de)
    db.commit()
    db.refresh(de)
    return de
