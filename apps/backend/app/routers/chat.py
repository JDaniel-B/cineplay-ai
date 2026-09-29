from fastapi import APIRouter, Request

from app.dependencies import CurrentUser, DbSession
from app.models import Conversation, Message, Movie, TokenUsage, VideoGame
from app.rate_limit import chat_limiter
from app.schemas import ChatInput, ChatOutput
from app.services.catalog_query import extract_filters, public_row, query_catalog
from app.services.llm import allocate_usage, count_unicode_words, generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/preguntar", response_model=ChatOutput)
def ask(payload: ChatInput, request: Request, user: CurrentUser, db: DbSession) -> ChatOutput:
    client_ip = request.client.host if request.client else "unknown"
    chat_limiter.check(f"{user.id_usuario}:{client_ip}")

    categories = (
        ["peliculas", "videojuegos"] if payload.categoria == "ambas" else [payload.categoria]
    )
    sources: dict[str, list[dict]] = {}
    for category in categories:
        model = Movie if category == "peliculas" else VideoGame
        filters = extract_filters(db, model, payload.pregunta)
        sources[category] = [public_row(row) for row in query_catalog(db, model, filters)]

    generated = generate_answer(payload.pregunta, sources)
    total_words = count_unicode_words(generated.exact_prompt) + count_unicode_words(generated.text)
    allocation = allocate_usage(total_words, sources)

    try:
        conversation = Conversation(id_usuario=user.id_usuario)
        db.add(conversation)
        db.flush()
        db.add_all(
            [
                Message(
                    id_conversacion=conversation.id_conversacion,
                    rol="usuario",
                    contenido=payload.pregunta,
                ),
                Message(
                    id_conversacion=conversation.id_conversacion,
                    rol="asistente",
                    contenido=generated.text,
                ),
                *[
                    TokenUsage(id_usuario=user.id_usuario, categoria=category, tokens=tokens)
                    for category, tokens in allocation.items()
                ],
            ]
        )
        db.commit()
        db.refresh(conversation)
    except Exception:
        db.rollback()
        raise

    return ChatOutput(
        respuesta=generated.text,
        fuentes=sources,
        id_conversacion=conversation.id_conversacion,
        consumo_palabras=total_words,
    )
