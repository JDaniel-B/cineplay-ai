from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import func, select

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import User
from app.rate_limit import login_limiter
from app.schemas import LoginInput, UserPublic
from app.security import DUMMY_HASH, create_session_token, verify_password

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=UserPublic)
def login(payload: LoginInput, request: Request, response: Response, db: DbSession) -> User:
    client_ip = request.client.host if request.client else "unknown"
    login_limiter.check(f"{client_ip}:{payload.correo.lower()}")
    user = db.scalar(select(User).where(func.lower(User.correo) == payload.correo.lower()))
    valid = verify_password(payload.password, user.password if user else DUMMY_HASH)
    if user is None or not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(user.id_usuario),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=8 * 60 * 60,
        path="/",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(get_settings().session_cookie_name, path="/")


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser) -> User:
    return user
