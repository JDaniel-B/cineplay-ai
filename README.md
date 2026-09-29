# CinePlay AI

Aplicación web full stack para consultar un catálogo de películas y videojuegos con lenguaje natural. El sistema filtra primero con consultas SQLAlchemy seguras y solo envía a Groq las filas relevantes; el modelo nunca genera ni ejecuta SQL.

## Arquitectura

```text
cineplay-ai/
├── apps/
│   ├── frontend/       Next.js 16, React 19, TypeScript, Tailwind, RHF/Zod, Recharts
│   └── backend/        FastAPI, SQLAlchemy, Alembic, LangChain/Groq
├── database/
│   └── schema.sql      Esquema SQLite equivalente a la migración inicial
├── package.json        Comandos reproducibles desde la raíz
└── pnpm-workspace.yaml
```

Se eligió SQLite porque el alcance es pequeño y así no se necesita crear ni operar otra base PostgreSQL en el VPS. La base local vive en `apps/backend/data/cineplay.db`, está ignorada por Git y activa claves foráneas y WAL. No se incluye Docker Compose porque no hay un servicio de base de datos que levantar.

El backend está organizado por routers, modelos, esquemas y servicios con responsabilidades reales. El frontend usa App Router, rutas agrupadas y componentes por funcionalidad siguiendo el patrón del monorepo de Consulting S.A.

## Requisitos

- Node.js 24.x
- pnpm 11.x
- Python 3.13.x

## Instalación desde cero en Windows/PowerShell

Desde la raíz del repositorio:

```powershell
pnpm install
python -m venv apps/backend/.venv
apps/backend/.venv/Scripts/python.exe -m pip install -e "apps/backend[dev]"
Copy-Item apps/backend/.env.example apps/backend/.env
Copy-Item apps/frontend/.env.local.example apps/frontend/.env.local
```

Edita `apps/backend/.env`. Genera un `JWT_SECRET` aleatorio, define contraseñas de al menos 10 caracteres en `ADMIN_PASSWORD` y, si quieres la cuenta normal de demostración, en `DEMO_USER_PASSWORD`. No confirmes esos archivos en Git.

Ejecuta migraciones y seed:

```powershell
pnpm db:migrate
pnpm db:seed
pnpm db:seed:catalog
```

Los seeds son idempotentes. El primero actualiza las cuentas configuradas e inserta el catálogo mínimo cuando las tablas están vacías. El segundo agrega 150 películas y 150 videojuegos ficticios y reproducibles, con variedad de géneros, plataformas, años y calificaciones. Los correos predeterminados son `admin@cineplay.example.com` y `usuario@cineplay.example.com`; las contraseñas son exclusivamente las que definas en tu `.env`.

## Desarrollo en VS Code

Después de instalar las dependencias, todo el entorno se levanta desde la raíz con un solo comando. Antes de iniciar, `predev` aplica las migraciones y el seed idempotente:

```powershell
pnpm dev
```

El backend y el frontend también conservan los comandos `pnpm dev:backend` y `pnpm dev:frontend` para depuración individual.

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger (solo desarrollo): http://localhost:8000/docs

## Groq y modo local

El valor predeterminado `LLM_MODE=mock` permite probar todo el flujo sin usar red ni una clave. El adaptador simulado redacta una respuesta determinista basada exclusivamente en las filas recuperadas.

Para el proveedor real:

```dotenv
LLM_MODE=groq
GROQ_API_KEY=tu_clave_rotada
GROQ_MODEL=openai/gpt-oss-20b
```

Confirma en tu cuenta de Groq que `GROQ_MODEL` siga disponible. El notebook de referencia contenía una clave Groq y credenciales PostgreSQL expuestas; ambas deben revocarse/rotarse y nunca reutilizarse.

## Flujo seguro de consultas

1. El cliente envía pregunta y categoría; el usuario se obtiene de la cookie HttpOnly.
2. Un intérprete determinista reconoce únicamente cantidad, género, plataforma, año, título y comparación de calificación.
3. SQLAlchemy crea consultas parametrizadas con límite máximo configurable. Para “mayor a 8.5” usa estrictamente `>`.
4. Solo la pregunta y las filas públicas relevantes forman el prompt de Groq.
5. Tras una respuesta válida, conversación, dos mensajes y consumo se guardan en una transacción.
6. Si Groq falla no se registra un éxito parcial.

No se envían usuarios, hashes, historial, credenciales ni tablas completas al modelo. Cada consulta es independiente.

## Conteo académico

`count_unicode_words` en `apps/backend/app/services/llm.py` cuenta secuencias alfanuméricas Unicode y permite apóstrofes internos. Se cuentan las palabras del prompt exacto (instrucciones, pregunta y filas) más la respuesta.

Cuando participan ambas categorías, el total se reparte proporcionalmente al número de palabras de las filas de cada categoría; cada peso tiene mínimo 1. La primera categoría recibe la división entera y la segunda el residuo, por lo que las dos filas siempre suman exactamente el total.

## Importar el SQL del docente

El SQL aún no está disponible y se desconocen su dialecto, claves y estrategia de inserción. Para evitar pérdida de datos no se automatiza una importación a ciegas.

Cuando recibas el archivo:

1. Haz una copia de `apps/backend/data/cineplay.db` con la API detenida.
2. Comparte el SQL para revisar nombres, tipos, rangos reales de calificación y claves.
3. Se creará una migración aditiva; no se usarán `DROP TABLE` ni recreaciones destructivas.
4. Si el archivo es PostgreSQL, sus tipos/secuencias se adaptarán a SQLite y los `INSERT` se convertirán a una estrategia idempotente basada en sus claves reales.
5. Después se ejecutarán pruebas de conteo, restricciones y consultas ejemplo antes de reemplazar el seed de desarrollo.

No ejecutes directamente un volcado PostgreSQL sobre SQLite.

## Seguridad implementada

- Argon2 para hashes y JWT de sesión en cookie HttpOnly, `SameSite=Lax`; `Secure=true` en producción.
- Sin registro público ni tokens en `localStorage`.
- Autorización administrativa en cada endpoint y también en la UI.
- No permite borrar la propia cuenta admin ni dejar el sistema sin administradores.
- CORS explícito y comprobación de `Origin` en operaciones mutables.
- Límites de longitud, filas, timeout/salida LLM y rate limit de login/chat.
- Errores legibles sin secretos y respuesta genérica para fallos inesperados.
- Historial y consumo siempre filtran por el usuario autenticado.

El rate limit actual vive en memoria y es apropiado para una sola instancia. Si se escala horizontalmente debe migrarse a Redis u otro almacén compartido.

## Verificación

```powershell
pnpm lint:backend
pnpm test:backend
pnpm check:frontend
```

Pruebas incluidas: permisos de usuario normal, filtro estricto de calificación, historial aislado, protección de último admin, validación de origen, conteo Unicode, reparto de consumo y cliente HTTP del frontend.

## Despliegue

Frontend: configura `NEXT_PUBLIC_API_URL` con la URL HTTPS pública del backend antes del build de Vercel.

Backend: monta `apps/backend/data` como volumen persistente, ejecuta `alembic upgrade head` antes de arrancar Uvicorn y define `COOKIE_SECURE=true`, un `JWT_SECRET` fuerte y `FRONTEND_ORIGINS` exacto. SQLite funciona para una instancia con carga moderada; si crece la concurrencia se puede migrar posteriormente a PostgreSQL conservando SQLAlchemy/Alembic.

## Guion de demostración (2–3 minutos)

1. Iniciar sesión como usuario normal y mostrar que no existe el menú Administración.
2. En Chat seleccionar Películas y preguntar “¿Cuáles son 3 películas de drama?”.
3. Seleccionar Videojuegos y preguntar “¿Qué juegos de disparos tienen una calificación mayor a 8.5?”.
4. Seleccionar Ambas y hacer una consulta combinada; señalar las fuentes del catálogo.
5. Abrir Historial y mostrar las preguntas independientes.
6. Abrir Consumo, aplicar fechas y explicar que son palabras académicas, no tokens facturados.
7. Cerrar sesión, entrar como admin y crear/editar/eliminar un usuario, una película y un videojuego.
8. Intentar una URL administrativa con usuario normal para demostrar el bloqueo del servidor.

## Pendientes externos

- SQL original del docente para adaptar el catálogo sin asumir claves ni tipos.
- Una `GROQ_API_KEY` nueva y el identificador de modelo habilitado para validar el proveedor real.
