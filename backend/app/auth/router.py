from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_active_user, require_roles
from app.auth.otp import create_otp, send_otp, verify_otp
from app.auth.schemas import (
    ConsentIn,
    LoginIn,
    MeOut,
    RegisterIn,
    TokenOut,
    VerifyOtpIn,
)
from app.auth.security import create_access_token, hash_password, verify_password
from app.config import settings
from app.db.session import get_db
from app.models import HoSoHocSinh, NguoiDung
from app.models.enums import MucDichOTP, TrangThaiNguoiDung, VaiTro

router = APIRouter(prefix="/auth", tags=["auth"])

DbDep = Annotated[Session, Depends(get_db)]


def _tim_nguoi_dung(db: Session, dinh_danh: str) -> NguoiDung | None:
    return db.scalar(
        select(NguoiDung).where(
            or_(NguoiDung.email == dinh_danh, NguoiDung.so_dien_thoai == dinh_danh)
        )
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: DbDep) -> dict[str, str]:
    if _tim_nguoi_dung(db, body.dinh_danh) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Định danh đã tồn tại")

    user = NguoiDung(
        email=body.email,
        so_dien_thoai=body.so_dien_thoai,
        hashed_password=hash_password(body.password),
        vai_tro=body.vai_tro,
        trang_thai=TrangThaiNguoiDung.cho_xac_thuc,
        la_vi_thanh_nien=body.la_vi_thanh_nien,
    )
    db.add(user)
    db.flush()

    if body.vai_tro == VaiTro.hoc_sinh:
        db.add(
            HoSoHocSinh(
                nguoi_dung_id=user.id,
                phan_khuc=body.phan_khuc,
                lop=body.lop,
                mon=body.mon,
                doi_tuyen=body.doi_tuyen,
            )
        )

    code = create_otp(db, body.dinh_danh, MucDichOTP.dang_ky)
    db.commit()
    send_otp(body.dinh_danh, code)
    resp = {"id": user.id, "message": "Đã gửi OTP để xác thực"}
    # CHỈ ở chế độ dev: trả mã để tiện thử (production tắt DEBUG → không lộ OTP).
    if settings.debug:
        resp["otp_dev"] = code
    return resp


@router.post("/verify-otp")
def verify_otp_endpoint(body: VerifyOtpIn, db: DbDep) -> dict[str, str]:
    ket_qua = verify_otp(db, body.dinh_danh, body.ma, MucDichOTP.dang_ky)
    if ket_qua != "ok":
        loi = {
            "het_han": "OTP đã hết hạn",
            "sai": "OTP không đúng",
            "khong_tim_thay": "Không tìm thấy OTP",
        }[ket_qua]
        raise HTTPException(status.HTTP_400_BAD_REQUEST, loi)

    user = _tim_nguoi_dung(db, body.dinh_danh)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy người dùng")
    user.trang_thai = TrangThaiNguoiDung.hoat_dong
    db.commit()
    return {"message": "Xác thực thành công"}


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: DbDep) -> TokenOut:
    user = _tim_nguoi_dung(db, body.dinh_danh)
    if (
        user is None
        or not user.hashed_password
        or not verify_password(body.password, user.hashed_password)
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sai thông tin đăng nhập")
    if user.trang_thai == TrangThaiNguoiDung.cho_xac_thuc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản chưa xác thực OTP")
    if user.trang_thai == TrangThaiNguoiDung.khoa:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản đã bị khóa")
    # Vị thành niên bắt buộc có đồng ý phụ huynh (FR-C03)
    if user.la_vi_thanh_nien and not user.dong_y_phu_huynh:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Tài khoản vị thành niên cần đồng ý phụ huynh"
        )
    return TokenOut(access_token=create_access_token(user.id, user.vai_tro.value))


@router.post("/parent-consent")
def parent_consent(
    body: ConsentIn,
    db: DbDep,
    parent: Annotated[NguoiDung, Depends(require_roles(VaiTro.phu_huynh))],
) -> dict[str, str]:
    child = db.get(NguoiDung, body.child_id)
    if child is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy học sinh")
    child.phu_huynh_id = parent.id
    child.dong_y_phu_huynh = True
    db.commit()
    return {"message": "Đã ghi nhận đồng ý phụ huynh"}


@router.get("/me", response_model=MeOut)
def me(user: Annotated[NguoiDung, Depends(get_current_active_user)]) -> NguoiDung:
    return user


@router.get("/admin-only")
def admin_only(
    user: Annotated[NguoiDung, Depends(require_roles(VaiTro.quan_tri))],
) -> dict[str, bool]:
    return {"ok": True}
