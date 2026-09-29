from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select

from app.dependencies import AdminUser, DbSession
from app.models import Movie, VideoGame
from app.schemas import MovieCreate, MoviePublic, Page, VideoGameCreate, VideoGamePublic

router = APIRouter(prefix="/admin", tags=["administración"])


def _page(
    model: type[Movie] | type[VideoGame], db: DbSession, page: int, page_size: int, buscar: str
) -> Page:
    filters = []
    if buscar:
        term = f"%{buscar.strip()}%"
        filters.append(
            or_(model.titulo.ilike(term), model.genero.ilike(term), model.plataforma.ilike(term))
        )
    total = db.scalar(select(func.count()).select_from(model).where(*filters)) or 0
    rows = db.scalars(
        select(model)
        .where(*filters)
        .order_by(model.titulo, model.id_pelicula if model is Movie else model.id_videojuego)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    schema = MoviePublic if model is Movie else VideoGamePublic
    return Page(
        items=[schema.model_validate(row).model_dump(mode="json") for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/peliculas", response_model=Page)
def list_movies(
    _admin: AdminUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    buscar: str = Query("", max_length=100),
) -> Page:
    return _page(Movie, db, page, page_size, buscar)


@router.post("/peliculas", response_model=MoviePublic, status_code=status.HTTP_201_CREATED)
def create_movie(payload: MovieCreate, _admin: AdminUser, db: DbSession) -> Movie:
    movie = Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.put("/peliculas/{item_id}", response_model=MoviePublic)
def update_movie(item_id: int, payload: MovieCreate, _admin: AdminUser, db: DbSession) -> Movie:
    movie = db.get(Movie, item_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    for key, value in payload.model_dump().items():
        setattr(movie, key, value)
    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/peliculas/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(item_id: int, _admin: AdminUser, db: DbSession) -> None:
    movie = db.get(Movie, item_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    db.delete(movie)
    db.commit()


@router.get("/videojuegos", response_model=Page)
def list_games(
    _admin: AdminUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    buscar: str = Query("", max_length=100),
) -> Page:
    return _page(VideoGame, db, page, page_size, buscar)


@router.post("/videojuegos", response_model=VideoGamePublic, status_code=status.HTTP_201_CREATED)
def create_game(payload: VideoGameCreate, _admin: AdminUser, db: DbSession) -> VideoGame:
    game = VideoGame(**payload.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.put("/videojuegos/{item_id}", response_model=VideoGamePublic)
def update_game(
    item_id: int, payload: VideoGameCreate, _admin: AdminUser, db: DbSession
) -> VideoGame:
    game = db.get(VideoGame, item_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    for key, value in payload.model_dump().items():
        setattr(game, key, value)
    db.commit()
    db.refresh(game)
    return game


@router.delete("/videojuegos/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(item_id: int, _admin: AdminUser, db: DbSession) -> None:
    game = db.get(VideoGame, item_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    db.delete(game)
    db.commit()
