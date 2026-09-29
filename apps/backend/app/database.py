from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import BACKEND_DIR, get_settings


class Base(DeclarativeBase):
    pass


def normalize_sqlite_url(url: str) -> str:
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        return f"sqlite:///{(BACKEND_DIR / url.removeprefix(prefix)).as_posix()}"
    return url


settings = get_settings()
database_url = normalize_sqlite_url(settings.database_url)
if database_url.startswith("sqlite:///"):
    Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False, "timeout": 15}
    if database_url.startswith("sqlite")
    else {},
)


@event.listens_for(Engine, "connect")
def configure_sqlite(dbapi_connection: object, _connection_record: object) -> None:
    if database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session]:
    with SessionLocal() as session:
        yield session
