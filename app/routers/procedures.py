from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Procedure
from app.schemas import ProcedureDetailOut, ProcedureOut

router = APIRouter(prefix="/api/procedures", tags=["procedures"])


@router.get("", response_model=list[ProcedureOut])
def list_procedures(db: Session = Depends(get_db)):
    """Lista todos los tramites activos (para la pantalla principal)."""
    return db.query(Procedure).filter(Procedure.is_active == 1).all()


@router.get("/{procedure_id}", response_model=ProcedureDetailOut)
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    """Detalle de un tramite puntual, con su checklist y fuentes."""
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if procedure is None:
        raise HTTPException(status_code=404, detail="Tramite no encontrado")
    return procedure
