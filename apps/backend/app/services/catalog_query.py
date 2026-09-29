import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Movie, VideoGame

NUMBER_WORDS = {
    "un": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


@dataclass(frozen=True)
class AllowedFilters:
    limit: int
    genre: str | None = None
    platform: str | None = None
    year: int | None = None
    rating_value: Decimal | None = None
    rating_operator: str | None = None
    title: str | None = None


def _known_match(question: str, values: list[str]) -> str | None:
    normalized = normalize(question)
    matches = [value for value in values if normalize(value) in normalized]
    return max(matches, key=len) if matches else None


def extract_filters(
    db: Session, model: type[Movie] | type[VideoGame], question: str
) -> AllowedFilters:
    text = normalize(question)
    max_rows = get_settings().chat_max_rows
    number_match = re.search(
        r"\b(\d{1,2}|un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\b", text
    )
    if number_match:
        raw = number_match.group(1)
        requested = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
    else:
        requested = min(10, max_rows)
    limit = max(1, min(requested, max_rows))

    genres = list(db.scalars(select(model.genero).distinct()).all())
    platforms = list(db.scalars(select(model.plataforma).distinct()).all())
    titles = list(db.scalars(select(model.titulo).distinct()).all())
    genre = _known_match(question, genres)
    platform = _known_match(question, platforms)

    year_match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", text)
    year = int(year_match.group(1)) if year_match else None

    rating = re.search(
        r"(?:calificacion|puntuacion|nota)?\s*(?:es\s*)?"
        r"(mayor|superior|mas de|menor|inferior|menos de)\s*"
        r"(?:a|que)?\s*(\d+(?:[.,]\d+)?)",
        text,
    )
    rating_value = Decimal(rating.group(2).replace(",", ".")) if rating else None
    rating_operator = (
        ">"
        if rating and rating.group(1) in {"mayor", "superior", "mas de"}
        else "<"
        if rating
        else None
    )

    title = _known_match(question, titles)
    title_match = re.search(r"(?:titulo|titulada?|llamad[oa])\s+[\"']?([^\"'?]+)", text)
    if title is None and title_match:
        title = title_match.group(1).strip()[:200]

    return AllowedFilters(limit, genre, platform, year, rating_value, rating_operator, title)


def query_catalog(
    db: Session, model: type[Movie] | type[VideoGame], filters: AllowedFilters
) -> list[Movie] | list[VideoGame]:
    query: Select = select(model)
    if filters.genre:
        query = query.where(func.lower(model.genero) == filters.genre.lower())
    if filters.platform:
        query = query.where(func.lower(model.plataforma) == filters.platform.lower())
    if filters.year:
        query = query.where(model.anio_lanzamiento == filters.year)
    if filters.title:
        query = query.where(model.titulo.ilike(f"%{filters.title}%"))
    if filters.rating_value is not None:
        query = query.where(
            model.calificacion > filters.rating_value
            if filters.rating_operator == ">"
            else model.calificacion < filters.rating_value
        )
    query = query.order_by(model.calificacion.desc(), model.titulo.asc()).limit(filters.limit)
    return list(db.scalars(query).all())


def public_row(row: Movie | VideoGame) -> dict:
    common = {
        "titulo": row.titulo,
        "genero": row.genero,
        "plataforma": row.plataforma,
        "anio_lanzamiento": row.anio_lanzamiento,
        "calificacion": float(row.calificacion),
    }
    if isinstance(row, Movie):
        return {
            **common,
            "director": row.director,
            "actores": row.actores,
            "productora": row.productora,
            "duracion_minutos": row.duracion_minutos,
            "clasificacion": row.clasificacion,
        }
    return {**common, "desarrollador": row.desarrollador, "jugadores": row.jugadores}
