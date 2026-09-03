"""
App entry point. Run it with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import chat, procedures

app = FastAPI(
    title="API - Asistente de Trámites de Córdoba",
    description="Backend del proyecto de beca de IA: RAG sobre trámites públicos.",
    version="0.1.0",
)

# Le permite al frontend de Next.js (en otro puerto) llamar a esta API.
# En produccion, reemplazar "*" por el dominio real del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas en la base de datos si todavia no existen.
Base.metadata.create_all(bind=engine)

app.include_router(procedures.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "API de trámites funcionando"}
