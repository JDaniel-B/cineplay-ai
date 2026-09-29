from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Movie, User, VideoGame
from app.security import hash_password


@pytest.fixture(autouse=True)
def force_mock_llm() -> Generator[None]:
    settings = get_settings()
    original_mode = settings.llm_mode
    settings.llm_mode = "mock"
    yield
    settings.llm_mode = original_mode


@pytest.fixture()
def db() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    with testing_session() as session:
        session.add_all(
            [
                User(
                    nombre="Admin",
                    correo="admin@example.com",
                    password=hash_password("password-admin"),
                    rol="admin",
                ),
                User(
                    nombre="Ana",
                    correo="ana@example.com",
                    password=hash_password("password-user1"),
                    rol="usuario",
                ),
                User(
                    nombre="Beto",
                    correo="beto@example.com",
                    password=hash_password("password-user2"),
                    rol="usuario",
                ),
                Movie(
                    titulo="Drama Uno",
                    genero="Drama",
                    plataforma="Max",
                    anio_lanzamiento=2020,
                    calificacion=Decimal("9.1"),
                    director="Directora",
                    actores="Actriz",
                    productora="Estudio",
                    duracion_minutos=110,
                    clasificacion="PG-13",
                ),
                Movie(
                    titulo="Drama Dos",
                    genero="Drama",
                    plataforma="Netflix",
                    anio_lanzamiento=2021,
                    calificacion=Decimal("8.7"),
                    director="Director",
                    actores="Actor",
                    productora="Estudio",
                    duracion_minutos=120,
                    clasificacion="PG",
                ),
                VideoGame(
                    titulo="DOOM Test",
                    genero="Disparos",
                    plataforma="PC",
                    anio_lanzamiento=2022,
                    calificacion=Decimal("8.8"),
                    desarrollador="Studio",
                    jugadores=1,
                ),
                VideoGame(
                    titulo="Disparo Bajo",
                    genero="Disparos",
                    plataforma="PC",
                    anio_lanzamiento=2020,
                    calificacion=Decimal("8.5"),
                    desarrollador="Studio",
                    jugadores=1,
                ),
            ]
        )
        session.commit()
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient]:
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> None:
    response = client.post("/auth/login", json={"correo": email, "password": password})
    assert response.status_code == 200, response.text
