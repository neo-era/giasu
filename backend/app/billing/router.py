from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user
from app.billing.plans import GIOI_HAN_NGAY
from app.billing.schemas import CheckoutIn, CheckoutOut, PlanOut, WebhookIn
from app.billing.service import (
    da_dung_hom_nay,
    lay_goi_hien_tai,
    tao_checkout,
    vietqr_payload,
    xac_nhan_thanh_toan,
)
from app.db.session import get_db
from app.models import NguoiDung

router = APIRouter(prefix="/billing", tags=["billing"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[NguoiDung, Depends(get_current_active_user)]


@router.get("/me", response_model=PlanOut)
def my_plan(db: DbDep, user: UserDep) -> PlanOut:
    goi = lay_goi_hien_tai(db, user)
    return PlanOut(
        goi=goi,
        gioi_han_ngay=GIOI_HAN_NGAY.get(goi),
        da_dung_hom_nay=da_dung_hom_nay(db, user),
    )


@router.post("/checkout", response_model=CheckoutOut, status_code=201)
def checkout(body: CheckoutIn, db: DbDep, user: UserDep) -> CheckoutOut:
    try:
        tt = tao_checkout(db, user, body.loai_goi)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return CheckoutOut(
        ma_giao_dich=tt.ma_giao_dich,
        so_tien=tt.so_tien,
        vietqr=vietqr_payload(tt),
    )


@router.post("/webhook")
def webhook(body: WebhookIn, db: DbDep) -> dict[str, str]:
    # TODO(B16+): xác thực chữ ký webhook ngân hàng trước khi tin.
    tt = xac_nhan_thanh_toan(db, body.ma_giao_dich)
    if tt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy giao dịch")
    return {"trang_thai": tt.trang_thai.value}
