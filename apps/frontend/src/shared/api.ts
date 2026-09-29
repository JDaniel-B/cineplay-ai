const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      "X-Requested-With": "CinePlayAI",
      ...init.headers,
    },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string | Array<{ msg: string }> }
      | null;
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((item) => item.msg).join(". ")
      : body?.detail;
    throw new ApiError(detail || "No se pudo completar la solicitud.", response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type User = {
  id_usuario: number;
  nombre: string;
  correo: string;
  rol: "usuario" | "admin";
  fecha_registro: string;
};

export type Page<T> = { items: T[]; total: number; page: number; page_size: number };

export type Movie = {
  id_pelicula: number;
  titulo: string;
  genero: string;
  plataforma: string;
  anio_lanzamiento: number;
  calificacion: number;
  director: string;
  actores: string;
  productora: string;
  duracion_minutos: number;
  clasificacion: string;
  fecha_registro: string;
};

export type VideoGame = {
  id_videojuego: number;
  titulo: string;
  genero: string;
  plataforma: string;
  anio_lanzamiento: number;
  calificacion: number;
  desarrollador: string;
  jugadores: number;
  fecha_registro: string;
};
