from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Todos los modelos (app/models.py) heredan de esta Base
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: opens one DB session per request and closes it
    automatically when it's done. Injected into endpoints with
    `Depends(get_db)`.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
