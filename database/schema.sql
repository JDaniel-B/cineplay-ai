PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INTEGER PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  correo VARCHAR(254) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  rol VARCHAR(20) NOT NULL CHECK (rol IN ('usuario', 'admin')),
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_usuarios_correo ON usuarios(correo);
CREATE INDEX IF NOT EXISTS ix_usuarios_rol ON usuarios(rol);

CREATE TABLE IF NOT EXISTS peliculas (
  id_pelicula INTEGER PRIMARY KEY,
  titulo VARCHAR(200) NOT NULL,
  genero VARCHAR(80) NOT NULL,
  plataforma VARCHAR(100) NOT NULL,
  anio_lanzamiento INTEGER NOT NULL CHECK (anio_lanzamiento BETWEEN 1888 AND 2200),
  calificacion NUMERIC(3,1) NOT NULL CHECK (calificacion BETWEEN 0 AND 10),
  director VARCHAR(150) NOT NULL,
  actores TEXT NOT NULL,
  productora VARCHAR(150) NOT NULL,
  duracion_minutos INTEGER NOT NULL CHECK (duracion_minutos > 0),
  clasificacion VARCHAR(30) NOT NULL,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_peliculas_titulo ON peliculas(titulo);
CREATE INDEX IF NOT EXISTS ix_peliculas_genero ON peliculas(genero);
CREATE INDEX IF NOT EXISTS ix_peliculas_plataforma ON peliculas(plataforma);
CREATE INDEX IF NOT EXISTS ix_peliculas_busqueda ON peliculas(genero, plataforma, anio_lanzamiento);

CREATE TABLE IF NOT EXISTS videojuegos (
  id_videojuego INTEGER PRIMARY KEY,
  titulo VARCHAR(200) NOT NULL,
  genero VARCHAR(80) NOT NULL,
  plataforma VARCHAR(100) NOT NULL,
  anio_lanzamiento INTEGER NOT NULL CHECK (anio_lanzamiento BETWEEN 1958 AND 2200),
  calificacion NUMERIC(3,1) NOT NULL CHECK (calificacion BETWEEN 0 AND 10),
  desarrollador VARCHAR(150) NOT NULL,
  jugadores INTEGER NOT NULL CHECK (jugadores > 0),
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_videojuegos_titulo ON videojuegos(titulo);
CREATE INDEX IF NOT EXISTS ix_videojuegos_genero ON videojuegos(genero);
CREATE INDEX IF NOT EXISTS ix_videojuegos_plataforma ON videojuegos(plataforma);
CREATE INDEX IF NOT EXISTS ix_videojuegos_busqueda ON videojuegos(genero, plataforma, anio_lanzamiento);

CREATE TABLE IF NOT EXISTS conversaciones (
  id_conversacion INTEGER PRIMARY KEY,
  id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_conversaciones_usuario_fecha ON conversaciones(id_usuario, fecha_creacion);

CREATE TABLE IF NOT EXISTS mensajes (
  id_mensaje INTEGER PRIMARY KEY,
  id_conversacion INTEGER NOT NULL REFERENCES conversaciones(id_conversacion) ON DELETE CASCADE,
  rol VARCHAR(20) NOT NULL CHECK (rol IN ('usuario', 'asistente')),
  contenido TEXT NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_mensajes_id_conversacion ON mensajes(id_conversacion);

CREATE TABLE IF NOT EXISTS consumo_tokens (
  id_consumo INTEGER PRIMARY KEY,
  id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('peliculas', 'videojuegos')),
  tokens INTEGER NOT NULL CHECK (tokens >= 0),
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_consumo_usuario_fecha ON consumo_tokens(id_usuario, fecha);
