"""Esquema inicial de CinePlay AI."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rol IN ('usuario', 'admin')", name="ck_usuarios_rol"),
        sa.UniqueConstraint("correo"),
    )
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"])
    op.create_index("ix_usuarios_rol", "usuarios", ["rol"])
    op.create_table(
        "peliculas",
        sa.Column("id_pelicula", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("genero", sa.String(80), nullable=False),
        sa.Column("plataforma", sa.String(100), nullable=False),
        sa.Column("anio_lanzamiento", sa.Integer(), nullable=False),
        sa.Column("calificacion", sa.Numeric(3, 1), nullable=False),
        sa.Column("director", sa.String(150), nullable=False),
        sa.Column("actores", sa.Text(), nullable=False),
        sa.Column("productora", sa.String(150), nullable=False),
        sa.Column("duracion_minutos", sa.Integer(), nullable=False),
        sa.Column("clasificacion", sa.String(30), nullable=False),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("calificacion >= 0 AND calificacion <= 10", name="ck_peliculas_calificacion"),
        sa.CheckConstraint("anio_lanzamiento >= 1888 AND anio_lanzamiento <= 2200", name="ck_peliculas_anio"),
        sa.CheckConstraint("duracion_minutos > 0", name="ck_peliculas_duracion"),
    )
    op.create_index("ix_peliculas_titulo", "peliculas", ["titulo"])
    op.create_index("ix_peliculas_genero", "peliculas", ["genero"])
    op.create_index("ix_peliculas_plataforma", "peliculas", ["plataforma"])
    op.create_index("ix_peliculas_busqueda", "peliculas", ["genero", "plataforma", "anio_lanzamiento"])
    op.create_table(
        "videojuegos",
        sa.Column("id_videojuego", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("genero", sa.String(80), nullable=False),
        sa.Column("plataforma", sa.String(100), nullable=False),
        sa.Column("anio_lanzamiento", sa.Integer(), nullable=False),
        sa.Column("calificacion", sa.Numeric(3, 1), nullable=False),
        sa.Column("desarrollador", sa.String(150), nullable=False),
        sa.Column("jugadores", sa.Integer(), nullable=False),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("calificacion >= 0 AND calificacion <= 10", name="ck_videojuegos_calificacion"),
        sa.CheckConstraint("anio_lanzamiento >= 1958 AND anio_lanzamiento <= 2200", name="ck_videojuegos_anio"),
        sa.CheckConstraint("jugadores > 0", name="ck_videojuegos_jugadores"),
    )
    op.create_index("ix_videojuegos_titulo", "videojuegos", ["titulo"])
    op.create_index("ix_videojuegos_genero", "videojuegos", ["genero"])
    op.create_index("ix_videojuegos_plataforma", "videojuegos", ["plataforma"])
    op.create_index("ix_videojuegos_busqueda", "videojuegos", ["genero", "plataforma", "anio_lanzamiento"])
    op.create_table(
        "conversaciones",
        sa.Column("id_conversacion", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversaciones_usuario_fecha", "conversaciones", ["id_usuario", "fecha_creacion"])
    op.create_table(
        "mensajes",
        sa.Column("id_mensaje", sa.Integer(), primary_key=True),
        sa.Column("id_conversacion", sa.Integer(), sa.ForeignKey("conversaciones.id_conversacion", ondelete="CASCADE"), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("fecha", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rol IN ('usuario', 'asistente')", name="ck_mensajes_rol"),
    )
    op.create_index("ix_mensajes_id_conversacion", "mensajes", ["id_conversacion"])
    op.create_table(
        "consumo_tokens",
        sa.Column("id_consumo", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False),
        sa.Column("categoria", sa.String(20), nullable=False),
        sa.Column("tokens", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("categoria IN ('peliculas', 'videojuegos')", name="ck_consumo_categoria"),
        sa.CheckConstraint("tokens >= 0", name="ck_consumo_tokens"),
    )
    op.create_index("ix_consumo_usuario_fecha", "consumo_tokens", ["id_usuario", "fecha"])


def downgrade() -> None:
    op.drop_table("consumo_tokens")
    op.drop_table("mensajes")
    op.drop_table("conversaciones")
    op.drop_table("videojuegos")
    op.drop_table("peliculas")
    op.drop_table("usuarios")
