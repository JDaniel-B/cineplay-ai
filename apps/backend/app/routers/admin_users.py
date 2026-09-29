from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from app.dependencies import AdminUser, DbSession
from app.models import User
from app.schemas import Page, UserCreate, UserPublic, UserUpdate
from app.security import hash_password

router = APIRouter(prefix="/admin/usuarios", tags=["administración"])


@router.get("", response_model=Page)
def list_users(
    _admin: AdminUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    buscar: str = Query("", max_length=100),
) -> Page:
    filters = []
    if buscar:
        term = f"%{buscar.strip()}%"
        filters.append(or_(User.nombre.ilike(term), User.correo.ilike(term)))
    total = db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
    rows = db.scalars(
        select(User)
        .where(*filters)
        .order_by(User.id_usuario)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return Page(
        items=[UserPublic.model_validate(row).model_dump(mode="json") for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, _admin: AdminUser, db: DbSession) -> User:
    user = User(
        nombre=payload.nombre.strip(),
        correo=payload.correo.lower(),
        password=hash_password(payload.password),
        rol=payload.rol,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo ya está registrado") from exc
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, payload: UserUpdate, admin: AdminUser, db: DbSession) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.rol == "admin" and payload.rol != "admin":
        admins = db.scalar(select(func.count()).select_from(User).where(User.rol == "admin")) or 0
        if admins <= 1:
            raise HTTPException(
                status_code=409, detail="El sistema debe conservar al menos un administrador"
            )
    user.nombre = payload.nombre.strip()
    user.correo = payload.correo.lower()
    user.rol = payload.rol
    if payload.password:
        user.password = hash_password(payload.password)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo ya está registrado") from exc
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: AdminUser, db: DbSession) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id_usuario == admin.id_usuario:
        raise HTTPException(status_code=409, detail="No puedes eliminar tu propia cuenta")
    if user.rol == "admin":
        admins = db.scalar(select(func.count()).select_from(User).where(User.rol == "admin")) or 0
        if admins <= 1:
            raise HTTPException(
                status_code=409, detail="El sistema debe conservar al menos un administrador"
            )
    db.delete(user)
    db.commit()
