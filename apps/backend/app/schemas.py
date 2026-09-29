from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserPublic(ORMModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    rol: Literal["usuario", "admin"]
    fecha_registro: datetime


class LoginInput(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=10, max_length=128)
    rol: Literal["usuario", "admin"] = "usuario"


class UserUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    rol: Literal["usuario", "admin"]
    password: str | None = Field(default=None, min_length=10, max_length=128)


class MovieBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    genero: str = Field(min_length=1, max_length=80)
    plataforma: str = Field(min_length=1, max_length=100)
    anio_lanzamiento: int = Field(ge=1888, le=2200)
    calificacion: Decimal = Field(ge=0, le=10, decimal_places=1)
    director: str = Field(min_length=1, max_length=150)
    actores: str = Field(min_length=1, max_length=2000)
    productora: str = Field(min_length=1, max_length=150)
    duracion_minutos: int = Field(gt=0, le=1000)
    clasificacion: str = Field(min_length=1, max_length=30)


class MovieCreate(MovieBase):
    pass


class MoviePublic(MovieBase, ORMModel):
    id_pelicula: int
    fecha_registro: datetime


class VideoGameBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    genero: str = Field(min_length=1, max_length=80)
    plataforma: str = Field(min_length=1, max_length=100)
    anio_lanzamiento: int = Field(ge=1958, le=2200)
    calificacion: Decimal = Field(ge=0, le=10, decimal_places=1)
    desarrollador: str = Field(min_length=1, max_length=150)
    jugadores: int = Field(gt=0, le=10000)


class VideoGameCreate(VideoGameBase):
    pass


class VideoGamePublic(VideoGameBase, ORMModel):
    id_videojuego: int
    fecha_registro: datetime


class Page(BaseModel):
    items: list[dict]
    total: int
    page: int
    page_size: int


class ChatInput(BaseModel):
    pregunta: str = Field(min_length=3, max_length=500)
    categoria: Literal["peliculas", "videojuegos", "ambas"]

    @field_validator("pregunta")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        return " ".join(value.split())


class ChatOutput(BaseModel):
    respuesta: str
    fuentes: dict[str, list[dict]]
    id_conversacion: int
    consumo_palabras: int


class HistoryItem(BaseModel):
    id_conversacion: int
    fecha: datetime
    pregunta: str
    respuesta: str


class HistoryPage(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int


class ConsumptionItem(BaseModel):
    categoria: Literal["peliculas", "videojuegos"]
    tokens: int


class ConsumptionSummary(BaseModel):
    items: list[ConsumptionItem]
    total: int
    desde: date | None
    hasta: date | None
