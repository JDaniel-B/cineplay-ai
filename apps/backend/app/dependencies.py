from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.security import decode_session_token

DbSession = Annotated[Session, Depends(get_db)]


def current_user(
    db: DbSession,
    session_cookie: Annotated[str | None, Cookie(alias=get_settings().session_cookie_name)] = None,
) -> User:
    user_id = decode_session_token(session_cookie) if session_cookie else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def admin_user(user: CurrentUser) -> User:
    if user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol administrador"
        )
    return user


AdminUser = Annotated[User, Depends(admin_user)]
