from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("rol IN ('usuario', 'admin')", name="ck_usuarios_rol"),)

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20), default="usuario", index=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    conversaciones: Mapped[list["Conversation"]] = relationship(cascade="all, delete-orphan")
    consumos: Mapped[list["TokenUsage"]] = relationship(cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "peliculas"
    __table_args__ = (
        CheckConstraint(
            "calificacion >= 0 AND calificacion <= 10", name="ck_peliculas_calificacion"
        ),
        CheckConstraint(
            "anio_lanzamiento >= 1888 AND anio_lanzamiento <= 2200", name="ck_peliculas_anio"
        ),
        CheckConstraint("duracion_minutos > 0", name="ck_peliculas_duracion"),
        Index("ix_peliculas_busqueda", "genero", "plataforma", "anio_lanzamiento"),
    )

    id_pelicula: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), index=True)
    genero: Mapped[str] = mapped_column(String(80), index=True)
    plataforma: Mapped[str] = mapped_column(String(100), index=True)
    anio_lanzamiento: Mapped[int]
    calificacion: Mapped[Decimal] = mapped_column(Numeric(3, 1))
    director: Mapped[str] = mapped_column(String(150))
    actores: Mapped[str] = mapped_column(Text)
    productora: Mapped[str] = mapped_column(String(150))
    duracion_minutos: Mapped[int]
    clasificacion: Mapped[str] = mapped_column(String(30))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class VideoGame(Base):
    __tablename__ = "videojuegos"
    __table_args__ = (
        CheckConstraint(
            "calificacion >= 0 AND calificacion <= 10", name="ck_videojuegos_calificacion"
        ),
        CheckConstraint(
            "anio_lanzamiento >= 1958 AND anio_lanzamiento <= 2200", name="ck_videojuegos_anio"
        ),
        CheckConstraint("jugadores > 0", name="ck_videojuegos_jugadores"),
        Index("ix_videojuegos_busqueda", "genero", "plataforma", "anio_lanzamiento"),
    )

    id_videojuego: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), index=True)
    genero: Mapped[str] = mapped_column(String(80), index=True)
    plataforma: Mapped[str] = mapped_column(String(100), index=True)
    anio_lanzamiento: Mapped[int]
    calificacion: Mapped[Decimal] = mapped_column(Numeric(3, 1))
    desarrollador: Mapped[str] = mapped_column(String(150))
    jugadores: Mapped[int]
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversaciones"
    __table_args__ = (Index("ix_conversaciones_usuario_fecha", "id_usuario", "fecha_creacion"),)

    id_conversacion: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    mensajes: Mapped[list["Message"]] = relationship(cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "mensajes"
    __table_args__ = (CheckConstraint("rol IN ('usuario', 'asistente')", name="ck_mensajes_rol"),)

    id_mensaje: Mapped[int] = mapped_column(primary_key=True)
    id_conversacion: Mapped[int] = mapped_column(
        ForeignKey("conversaciones.id_conversacion", ondelete="CASCADE"), index=True
    )
    rol: Mapped[str] = mapped_column(String(20))
    contenido: Mapped[str] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TokenUsage(Base):
    __tablename__ = "consumo_tokens"
    __table_args__ = (
        CheckConstraint("categoria IN ('peliculas', 'videojuegos')", name="ck_consumo_categoria"),
        CheckConstraint("tokens >= 0", name="ck_consumo_tokens"),
        Index("ix_consumo_usuario_fecha", "id_usuario", "fecha"),
    )

    id_consumo: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    categoria: Mapped[str] = mapped_column(String(20))
    tokens: Mapped[int]
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
