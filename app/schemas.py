"""
Schemas de Pydantic: definen que forma tiene cada request/response de la API.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RequirementOut(BaseModel):
    id: int
    description: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class OfficialSourceOut(BaseModel):
    id: int
    title: str
    url: str
    verified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcedureOut(BaseModel):
    id: int
    name: str
    short_description: str | None
    category: str | None
    agency: str | None

    model_config = ConfigDict(from_attributes=True)


class ProcedureDetailOut(ProcedureOut):
    requirements: list[RequirementOut] = []
    sources: list[OfficialSourceOut] = []


class ChatRequest(BaseModel):
    procedure_id: int
    question: str


class CitedSource(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    cited_sources: list[CitedSource]
    disclaimer: str = (
        "Esta informacion fue verificada al momento de cargarla, pero puede "
        "cambiar. Confirma siempre en la fuente oficial antes de presentarte "
        "a hacer el tramite."
    )
