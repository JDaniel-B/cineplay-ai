from datetime import date, datetime, time

from fastapi import APIRouter, Query
from sqlalchemy import case, func, select

from app.dependencies import CurrentUser, DbSession
from app.models import Conversation, Message, TokenUsage
from app.schemas import ConsumptionItem, ConsumptionSummary, HistoryItem, HistoryPage

router = APIRouter(tags=["cuenta"])


@router.get("/historial", response_model=HistoryPage)
def history(
    user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
) -> HistoryPage:
    total = (
        db.scalar(
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.id_usuario == user.id_usuario)
        )
        or 0
    )
    question = func.max(case((Message.rol == "usuario", Message.contenido)))
    answer = func.max(case((Message.rol == "asistente", Message.contenido)))
    rows = db.execute(
        select(Conversation.id_conversacion, Conversation.fecha_creacion, question, answer)
        .join(Message)
        .where(Conversation.id_usuario == user.id_usuario)
        .group_by(Conversation.id_conversacion)
        .order_by(Conversation.fecha_creacion.desc(), Conversation.id_conversacion.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return HistoryPage(
        items=[
            HistoryItem(id_conversacion=row[0], fecha=row[1], pregunta=row[2], respuesta=row[3])
            for row in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/consumo/resumen", response_model=ConsumptionSummary)
def consumption(
    user: CurrentUser,
    db: DbSession,
    desde: date | None = None,
    hasta: date | None = None,
) -> ConsumptionSummary:
    query = select(TokenUsage.categoria, func.sum(TokenUsage.tokens)).where(
        TokenUsage.id_usuario == user.id_usuario
    )
    if desde:
        query = query.where(TokenUsage.fecha >= datetime.combine(desde, time.min))
    if hasta:
        query = query.where(TokenUsage.fecha <= datetime.combine(hasta, time.max))
    values = dict(db.execute(query.group_by(TokenUsage.categoria)).all())
    items = [
        ConsumptionItem(categoria=category, tokens=int(values.get(category, 0)))
        for category in ("peliculas", "videojuegos")
    ]
    return ConsumptionSummary(
        items=items, total=sum(item.tokens for item in items), desde=desde, hasta=hasta
    )
