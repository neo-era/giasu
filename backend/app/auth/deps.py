from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_token
from app.db.session import get_db
from app.models import NguoiDung
from app.models.enums import TrangThaiNguoiDung, VaiTro

bearer = HTTPBearer(auto_error=True)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> NguoiDung:
    try:
        payload = decode_token(creds.credentials)
    except Exception as exc:  # token sai/het han
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ"
        ) from exc

    user = db.get(NguoiDung, payload.get("sub"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Không tìm thấy người dùng"
        )
    return user


def get_current_active_user(
    user: Annotated[NguoiDung, Depends(get_current_user)],
) -> NguoiDung:
    if user.trang_thai != TrangThaiNguoiDung.hoat_dong:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản chưa kích hoạt"
        )
    return user


def require_roles(*roles: VaiTro) -> Callable[..., NguoiDung]:
    """Dependency factory: chỉ cho phép các vai trò chỉ định (RBAC, FR-C01)."""

    def checker(
        user: Annotated[NguoiDung, Depends(get_current_active_user)],
    ) -> NguoiDung:
        if user.vai_tro not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền")
        return user

    return checker
