from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import answer_question

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal del proyecto: recibe una pregunta libre sobre un
    tramite puntual y devuelve una respuesta anclada en fuentes oficiales.
    """
    result = answer_question(db, request.procedure_id, request.question)
    return ChatResponse(
        answer=result["answer"],
        cited_sources=result["cited_sources"],
    )
