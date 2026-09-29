from decimal import Decimal

from sqlalchemy import func, select

from app.config import get_settings
from app.database import SessionLocal
from app.models import Movie, User, VideoGame
from app.security import hash_password

MOVIES = [
    {
        "titulo": "El padrino",
        "genero": "Drama",
        "plataforma": "Paramount+",
        "anio_lanzamiento": 1972,
        "calificacion": Decimal("9.2"),
        "director": "Francis Ford Coppola",
        "actores": "Marlon Brando, Al Pacino",
        "productora": "Paramount Pictures",
        "duracion_minutos": 175,
        "clasificacion": "R",
    },
    {
        "titulo": "Parásitos",
        "genero": "Drama",
        "plataforma": "Max",
        "anio_lanzamiento": 2019,
        "calificacion": Decimal("8.5"),
        "director": "Bong Joon-ho",
        "actores": "Song Kang-ho, Lee Sun-kyun",
        "productora": "Barunson E&A",
        "duracion_minutos": 132,
        "clasificacion": "R",
    },
    {
        "titulo": "Interestelar",
        "genero": "Ciencia ficción",
        "plataforma": "Netflix",
        "anio_lanzamiento": 2014,
        "calificacion": Decimal("8.7"),
        "director": "Christopher Nolan",
        "actores": "Matthew McConaughey, Anne Hathaway",
        "productora": "Warner Bros.",
        "duracion_minutos": 169,
        "clasificacion": "PG-13",
    },
]

GAMES = [
    {
        "titulo": "The Legend of Zelda: Breath of the Wild",
        "genero": "Aventura",
        "plataforma": "Nintendo Switch",
        "anio_lanzamiento": 2017,
        "calificacion": Decimal("9.7"),
        "desarrollador": "Nintendo",
        "jugadores": 1,
    },
    {
        "titulo": "It Takes Two",
        "genero": "Aventura",
        "plataforma": "PC",
        "anio_lanzamiento": 2021,
        "calificacion": Decimal("8.9"),
        "desarrollador": "Hazelight Studios",
        "jugadores": 2,
    },
    {
        "titulo": "DOOM Eternal",
        "genero": "Disparos",
        "plataforma": "PC",
        "anio_lanzamiento": 2020,
        "calificacion": Decimal("8.8"),
        "desarrollador": "id Software",
        "jugadores": 1,
    },
]


def upsert_user(db, email: str, name: str, password: str, role: str) -> None:
    user = db.scalar(select(User).where(func.lower(User.correo) == email.lower()))
    if user is None:
        db.add(User(nombre=name, correo=email.lower(), password=hash_password(password), rol=role))
    else:
        user.nombre = name
        user.password = hash_password(password)
        user.rol = role


def main() -> None:
    settings = get_settings()
    if not settings.admin_password:
        raise SystemExit("Define ADMIN_PASSWORD (mínimo 10 caracteres) antes de ejecutar el seed.")
    if len(settings.admin_password) < 10:
        raise SystemExit("ADMIN_PASSWORD debe tener al menos 10 caracteres.")
    with SessionLocal() as db:
        upsert_user(db, settings.admin_email, settings.admin_name, settings.admin_password, "admin")
        if settings.demo_user_password:
            if len(settings.demo_user_password) < 10:
                raise SystemExit("DEMO_USER_PASSWORD debe tener al menos 10 caracteres.")
            upsert_user(
                db,
                settings.demo_user_email,
                settings.demo_user_name,
                settings.demo_user_password,
                "usuario",
            )
        if (db.scalar(select(func.count()).select_from(Movie)) or 0) == 0:
            db.add_all(Movie(**item) for item in MOVIES)
        if (db.scalar(select(func.count()).select_from(VideoGame)) or 0) == 0:
            db.add_all(VideoGame(**item) for item in GAMES)
        db.commit()
    print("Seed aplicado de forma idempotente.")


if __name__ == "__main__":
    main()
