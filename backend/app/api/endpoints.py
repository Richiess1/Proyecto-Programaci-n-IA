from fastapi import APIRouter, Depends, HTTPException  # type: ignore[import]
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.schemas import evaluacion as schemas
from app.services import evaluacion_service
from typing import List

router = APIRouter()

@router.post("/ideas", response_model=schemas.Idea)
def crear_idea(idea: schemas.Idea, db: Session = Depends(get_db)): # <-- Cambiamos IdeaCreate por Idea
    # exclude_none=True evita enviar "id": None a la base de datos, 
    # permitiendo que SQLAlchemy genere el UUID automáticamente.
    db_idea = models.Idea(**idea.model_dump(exclude_none=True))
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

@router.get("/ideas", response_model=List[schemas.Idea])
def obtener_ideas(db: Session = Depends(get_db)):
    return db.query(models.Idea).all()

@router.get("/ideas/{idea_id}", response_model=schemas.Idea)
def obtener_idea(idea_id: str, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
         raise HTTPException(status_code=404, detail="Idea no encontrada")
    return idea

@router.post("/ideas/{idea_id}/evaluar", response_model=schemas.Evaluacion)
def evaluar_idea_endpoint(idea_id: str, db: Session = Depends(get_db)):
    try:
        return evaluacion_service.procesar_evaluacion(db, idea_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/ideas/{idea_id}/evaluaciones", response_model=List[schemas.Evaluacion])
def obtener_evaluaciones(idea_id: str, db: Session = Depends(get_db)):
    return db.query(models.Evaluacion).filter(models.Evaluacion.idea_id == idea_id).all()

@router.patch("/evaluaciones/{evaluacion_id}/estado", response_model=schemas.Evaluacion)
def actualizar_estado(evaluacion_id: str, estado_upd: schemas.EstadoUpdate, db: Session = Depends(get_db)):
    evaluacion = db.query(models.Evaluacion).filter(models.Evaluacion.id == evaluacion_id).first()
    if not evaluacion:
         raise HTTPException(status_code=404, detail="Evaluacion no encontrada")
    evaluacion.estado = estado_upd.estado
    db.commit()
    db.refresh(evaluacion)
    return evaluacion

@router.post("/comparar", response_model=schemas.Comparacion)
def comparar_ideas(req: schemas.ComparacionReq, db: Session = Depends(get_db)):
    return evaluacion_service.generar_comparacion(db, req.idea_ids)