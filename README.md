# API - Asistente de Trámites de Córdoba

Backend del proyecto de beca de IA. Implementa RAG (Retrieval-Augmented
Generation) sobre trámites públicos de Córdoba: cada respuesta se genera
únicamente a partir de fragmentos de fuentes oficiales verificadas, y siempre
se citan esas fuentes.

**Hecho en este scaffold:**
- Estructura completa del backend (FastAPI + SQLAlchemy + pgvector)
- Modelo de datos: `Tramite`, `Requisito`, `FuenteOficial`, `Chunk`
- Pipeline de RAG completo (`app/services/rag.py`)
- Endpoints: listar trámites, detalle de un trámite, chat (RAG)
- Los 5 trámites cargados con contenido real, verificado en fuentes oficiales:
  - Renovación de licencia de conducir - cordoba.gob.ar
  - Duplicado de DNI - argentina.gob.ar
  - Partida de nacimiento - registrocivil.cba.gov.ar
  - Patentamiento vehicular - argentina.gob.ar
  - Asignación Universal por Hijo - anses.gob.ar

## Cómo correrlo

### 1. Base de datos (Supabase, gratis)

1. Creá una cuenta en [supabase.com](https://supabase.com) y un proyecto nuevo
2. En el **SQL Editor** de Supabase, corré: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Copiá tu connection string desde *Project Settings > Database > Connection string* (modo *Session pooler*)

### 2. Variables de entorno

```bash
cp .env.example .env
```

Completá `.env` con:
- `DATABASE_URL`: la connection string de Supabase
- `GEMINI_API_KEY`: tu API key gratuita de [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 3. Instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Cargar los datos iniciales

```bash
python -m app.seed_data
```

### 5. Levantar el servidor

```bash
uvicorn app.main:app --reload
```

En `http://localhost:8000/docs` FastAPI genera automáticamente
documentación interactiva (Swagger) de todos los endpoints.

### 6. Probar el RAG

En `/docs`, se puede probar, por ejemplo, `POST /api/chat` con body:
```json
{
  "tramite_id": 1,
  "pregunta": "¿Qué necesito para renovar mi licencia de conducir?"
}
```

Deberías recibir una respuesta generada a partir del contenido real cargado,
con la fuente citada.

## Estructura del proyecto

```
app/
├── main.py              # arranque de la app, CORS, rutas
├── config.py             # variables de entorno tipadas
├── database.py            # conexión a Postgres
├── models.py               # tablas (SQLAlchemy)
├── schemas.py                # forma de los requests/responses (Pydantic)
├── seed_data.py                # carga de datos iniciales
├── routers/
│   ├── tramites.py               # GET /api/tramites, GET /api/tramites/{id}
│   └── chat.py                    # POST /api/chat (el endpoint de RAG)
└── services/
    ├── gemini_client.py            # wrapper de la API de Gemini
    └── rag.py                       # retrieval + prompt + generación
```
