"""
Estructura pensada para el RAG:

Tramite            -> un tramite puntual (ej: "Renovacion de licencia de conducir")
  -> Requisito      -> cada item del checklist de ese tramite (para la UI)
  -> FuenteOficial   -> de donde sale la informacion (para citar la fuente)
  -> Chunk            -> fragmentos de texto de esas fuentes, ya con su embedding,
                          listos para la busqueda semantica (RAG)
"""
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.database import Base


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    short_description = Column(String(500))
    category = Column(String(50))  # "municipal" | "provincial" | "nacional"
    agency = Column(String(200))  # e.g. "Municipalidad de Córdoba", "RENAPER"
    is_active = Column(Integer, default=1)  # 1 = visible in the app, 0 = disabled

    requirements = relationship("Requirement", back_populates="procedure", cascade="all, delete-orphan")
    sources = relationship("OfficialSource", back_populates="procedure", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="procedure", cascade="all, delete-orphan")


class Requirement(Base):
    """Each checklist item the user sees and can check off in the frontend."""

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    description = Column(String(300), nullable=False)
    order = Column(Integer, default=0)

    procedure = relationship("Procedure", back_populates="requirements")


class OfficialSource(Base):
    """The verified official source (to cite 'according to such .gob.ar site...')."""

    __tablename__ = "official_sources"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    title = Column(String(300), nullable=False)
    url = Column(String(500), nullable=False)
    verified_at = Column(DateTime, server_default=func.now())

    procedure = relationship("Procedure", back_populates="sources")


class Chunk(Base):
    """
    Text fragment (from an OfficialSource) + its embedding.
    This is the minimal unit the RAG pipeline retrieves to answer a question.
    """

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("official_sources.id"), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.embedding_dimensions))

    procedure = relationship("Procedure", back_populates="chunks")
