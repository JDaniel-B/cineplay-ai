"""Genera un catálogo amplio, ficticio y reproducible para pruebas locales."""

from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Movie, VideoGame

MOVIE_PREFIXES = [
    "Ecos",
    "Sombras",
    "Secretos",
    "Crónicas",
    "Luces",
    "El guardián",
    "La ruta",
    "Memorias",
    "Más allá",
    "El misterio",
    "Historias",
    "El último viaje",
    "Sueños",
    "La ciudad",
    "Voces",
]
MOVIE_SUFFIXES = [
    "del amanecer",
    "de cristal",
    "del océano",
    "sin tiempo",
    "de la montaña",
    "en la niebla",
    "del futuro",
    "bajo las estrellas",
    "del bosque",
    "de medianoche",
]
MOVIE_GENRES = [
    "Drama",
    "Acción",
    "Comedia",
    "Ciencia ficción",
    "Terror",
    "Romance",
    "Animación",
    "Documental",
    "Suspenso",
    "Fantasía",
    "Aventura",
    "Crimen",
]
MOVIE_PLATFORMS = ["Netflix", "Max", "Disney+", "Prime Video", "Apple TV+", "Paramount+"]
DIRECTORS = [
    "Lucía Herrera",
    "Mateo Salazar",
    "Sofía Castillo",
    "Daniel Robles",
    "Valeria Montes",
    "Andrés Vega",
    "Camila Fuentes",
    "Gabriel Ríos",
]
ACTORS = [
    "Elena Cruz, Martín Reyes",
    "Paula Soto, Diego Lunares",
    "Andrea Paz, Tomás Vidal",
    "Clara León, Bruno Campos",
    "Natalia Mora, Samuel Ruiz",
]
STUDIOS = ["Luz Norte Films", "Horizonte Studios", "Nebula Pictures", "Quetzal Cine"]
CLASSIFICATIONS = ["ATP", "PG", "PG-13", "R"]

GAME_PREFIXES = [
    "Guardianes",
    "Leyendas",
    "Horizonte",
    "Reinos",
    "Operación",
    "Viajeros",
    "Código",
    "Arena",
    "Mundos",
    "El despertar",
    "Frontera",
    "Imperio",
    "Rumbo",
    "Tormenta",
    "Nexo",
]
GAME_SUFFIXES = [
    "de Aether",
    "del vacío",
    "de neón",
    "sin fronteras",
    "del dragón",
    "estelar",
    "de acero",
    "del bosque eterno",
    "de los titanes",
    "infinito",
]
GAME_GENRES = [
    "Disparos",
    "Aventura",
    "RPG",
    "Estrategia",
    "Deportes",
    "Carreras",
    "Simulación",
    "Terror",
    "Plataformas",
    "Puzzle",
    "Acción",
    "MMO",
]
GAME_PLATFORMS = ["PC", "PlayStation 5", "Xbox Series", "Nintendo Switch", "Móvil"]
DEVELOPERS = [
    "Aurora Interactive",
    "Pixel Forge",
    "Quetzal Games",
    "Nebula Works",
    "Iron Harbor",
    "Luna Digital",
]


def build_movies() -> list[Movie]:
    movies: list[Movie] = []
    for index, (prefix, suffix) in enumerate(
        ((prefix, suffix) for prefix in MOVIE_PREFIXES for suffix in MOVIE_SUFFIXES),
        start=1,
    ):
        movies.append(
            Movie(
                titulo=f"{prefix} {suffix}",
                genero=MOVIE_GENRES[(index - 1) % len(MOVIE_GENRES)],
                plataforma=MOVIE_PLATFORMS[(index * 5) % len(MOVIE_PLATFORMS)],
                anio_lanzamiento=1980 + (index * 7) % 46,
                calificacion=Decimal(60 + (index * 13) % 40) / 10,
                director=DIRECTORS[(index * 3) % len(DIRECTORS)],
                actores=ACTORS[(index * 7) % len(ACTORS)],
                productora=STUDIOS[(index * 11) % len(STUDIOS)],
                duracion_minutos=82 + (index * 9) % 99,
                clasificacion=CLASSIFICATIONS[index % len(CLASSIFICATIONS)],
            )
        )
    return movies


def build_games() -> list[VideoGame]:
    games: list[VideoGame] = []
    for index, (prefix, suffix) in enumerate(
        ((prefix, suffix) for prefix in GAME_PREFIXES for suffix in GAME_SUFFIXES),
        start=1,
    ):
        games.append(
            VideoGame(
                titulo=f"{prefix} {suffix}",
                genero=GAME_GENRES[(index - 1) % len(GAME_GENRES)],
                plataforma=GAME_PLATFORMS[(index * 3) % len(GAME_PLATFORMS)],
                anio_lanzamiento=1990 + (index * 5) % 36,
                calificacion=Decimal(60 + (index * 17) % 40) / 10,
                desarrollador=DEVELOPERS[(index * 7) % len(DEVELOPERS)],
                jugadores=1 + (index * 3) % 64,
            )
        )
    return games


def main() -> None:
    with SessionLocal() as db:
        existing_movies = {title.casefold() for title in db.scalars(select(Movie.titulo))}
        existing_games = {title.casefold() for title in db.scalars(select(VideoGame.titulo))}

        movies = [
            movie for movie in build_movies() if movie.titulo.casefold() not in existing_movies
        ]
        games = [game for game in build_games() if game.titulo.casefold() not in existing_games]
        db.add_all([*movies, *games])
        db.commit()

    print(f"Catálogo amplio aplicado: {len(movies)} películas y {len(games)} videojuegos nuevos.")


if __name__ == "__main__":
    main()
