from google import genai
from google.genai import types

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Convierte un texto en un vector numerico (embedding).

    task_type:
      - "RETRIEVAL_DOCUMENT" cuando estamos indexando contenido de la base de
        conocimiento (los chunks de las normas).
      - "RETRIEVAL_QUERY" cuando estamos embebiendo la pregunta del usuario.
    Usar el task_type correcto mejora bastante la calidad de la busqueda.
    """
    response = _client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=settings.embedding_dimensions,
        ),
    )
    return response.embeddings[0].values


def generate_answer(prompt: str) -> str:
    """Le pide al LLM que genere texto a partir de un prompt ya armado."""
    response = _client.models.generate_content(
        model=settings.gemini_llm_model,
        contents=prompt,
    )
    return response.text
