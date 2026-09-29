import json
import re
from dataclasses import dataclass

from fastapi import HTTPException, status
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_settings

SYSTEM_INSTRUCTIONS = """Eres el asistente de CinePlay AI.
Responde en español y únicamente con los datos del catálogo incluidos abajo.
No inventes títulos, calificaciones ni atributos. Respeta la cantidad solicitada.
Si no hay coincidencias, dilo claramente. Si hay dos categorías, sepáralas con claridad.
La consulta es independiente y no existe conversación previa."""


@dataclass(frozen=True)
class GeneratedAnswer:
    text: str
    exact_prompt: str


def build_prompt(question: str, sources: dict[str, list[dict]]) -> str:
    sections = []
    for category, rows in sources.items():
        sections.append(f"{category.upper()}:\n{json.dumps(rows, ensure_ascii=False)}")
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\nDATOS DEL CATÁLOGO:\n"
        + "\n\n".join(sections)
        + f"\n\nPREGUNTA:\n{question}"
    )


def _mock_answer(sources: dict[str, list[dict]]) -> str:
    if not any(sources.values()):
        return "No encontré coincidencias en el catálogo para los filtros solicitados."
    blocks: list[str] = []
    for category, rows in sources.items():
        if not rows:
            blocks.append(f"{category.capitalize()}: no hay coincidencias.")
            continue
        label = "Películas" if category == "peliculas" else "Videojuegos"
        details = "; ".join(
            f"{row['titulo']} ({row['anio_lanzamiento']}), calificación {row['calificacion']}"
            for row in rows
        )
        blocks.append(f"{label}: {details}.")
    return " ".join(blocks)


def generate_answer(question: str, sources: dict[str, list[dict]]) -> GeneratedAnswer:
    settings = get_settings()
    prompt_text = build_prompt(question, sources)
    if settings.llm_mode == "mock":
        return GeneratedAnswer(_mock_answer(sources), prompt_text)
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Groq no está configurado. Define GROQ_API_KEY o usa LLM_MODE=mock.",
        )
    try:
        from langchain_groq import ChatGroq

        prompt = ChatPromptTemplate.from_messages([("user", "{content}")])
        model = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            timeout=settings.llm_timeout_seconds,
            max_tokens=settings.llm_max_tokens,
            temperature=0,
            max_retries=1,
        )
        result = model.invoke(prompt.format_messages(content=prompt_text))
        answer = str(result.content).strip()
        if not answer:
            raise ValueError("El proveedor devolvió una respuesta vacía")
        return GeneratedAnswer(answer, prompt_text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor de IA no pudo completar la consulta.",
        ) from exc


def count_unicode_words(text: str) -> int:
    """Cuenta secuencias Unicode alfanuméricas, permitiendo apóstrofes internos."""
    return len(re.findall(r"[^\W_]+(?:['’][^\W_]+)*", text, flags=re.UNICODE))


def allocate_usage(total: int, sources: dict[str, list[dict]]) -> dict[str, int]:
    categories = list(sources)
    if len(categories) == 1:
        return {categories[0]: total}
    weights = {
        category: max(1, count_unicode_words(json.dumps(rows, ensure_ascii=False)))
        for category, rows in sources.items()
    }
    first = categories[0]
    first_tokens = total * weights[first] // sum(weights.values())
    return {first: first_tokens, categories[1]: total - first_tokens}
