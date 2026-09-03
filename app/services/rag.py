"""
El corazon tecnico del proyecto: Retrieval-Augmented Generation (RAG).

Flujo:
1. Convertimos la pregunta del usuario en un embedding.
2. Buscamos en Postgres (pgvector) los fragmentos de fuentes oficiales mas
   parecidos semanticamente a esa pregunta (busqueda por significado, no por
   palabra literal).
3. Le pasamos esos fragmentos al LLM como UNICO contexto permitido, para que
   la respuesta este anclada en fuentes verificadas y no inventada.
4. Devolvemos la respuesta + qué fuentes se citaron, para mostrarlas en el
   frontend con trazabilidad.
"""
from sqlalchemy.orm import Session

from app.models import Chunk, OfficialSource
from app.services.gemini_client import embed_text, generate_answer

TOP_K = 5

PROMPT_TEMPLATE = """Sos un asistente que ayuda a ciudadanos de Cordoba, Argentina a entender tramites publicos.

Reglas estrictas que tenes que seguir siempre:
1. Responde UNICAMENTE en base a los fragmentos de fuentes oficiales de abajo. No uses conocimiento previo tuyo sobre el tema.
2. Si los fragmentos no alcanzan para responder con certeza, decilo explicitamente en vez de inventar una respuesta.
3. Usa un lenguaje simple y cercano (voseo argentino), sin tecnicismos innecesarios.
4. Se concreto y accionable: priorizá decirle a la persona que tiene que hacer.

Fragmentos de fuentes oficiales verificadas:
{context}

Pregunta del usuario: {question}

Respuesta:"""


def _find_relevant_chunks(db: Session, procedure_id: int, question: str) -> list[Chunk]:
    query_embedding = embed_text(question, task_type="RETRIEVAL_QUERY")
    return (
        db.query(Chunk)
        .filter(Chunk.procedure_id == procedure_id)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(TOP_K)
        .all()
    )


def _build_prompt(question: str, chunks: list[Chunk]) -> str:
    context = "\n\n".join(f"[Fragmento {i + 1}]\n{c.content}" for i, c in enumerate(chunks))
    return PROMPT_TEMPLATE.format(context=context, question=question)


def answer_question(db: Session, procedure_id: int, question: str) -> dict:
    chunks = _find_relevant_chunks(db, procedure_id, question)

    if not chunks:
        return {
            "answer": (
                "Todavia no tengo informacion cargada sobre este tramite. "
                "Te recomiendo consultar directamente la fuente oficial."
            ),
            "cited_sources": [],
        }

    prompt = _build_prompt(question, chunks)
    answer = generate_answer(prompt)

    source_ids = {c.source_id for c in chunks if c.source_id is not None}
    sources = db.query(OfficialSource).filter(OfficialSource.id.in_(source_ids)).all()

    return {
        "answer": answer,
        "cited_sources": [{"title": s.title, "url": s.url} for s in sources],
    }
