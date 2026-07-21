from sqlalchemy.orm import Session
from app.db import models
from app.schemas import evaluacion as schemas  # <-- Cambio de import
from app.ia.motor_ia import evaluar_idea

def procesar_evaluacion(db: Session, idea_id: str) -> models.Evaluacion:
    idea_db = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea_db:
        raise ValueError("Idea no encontrada")

    # Convierte a dict para enviarlo al motor
    idea_dict = {c.name: getattr(idea_db, c.name) for c in idea_db.__table__.columns}

    # Llama al motor de IA
    evaluacion_ia = evaluar_idea(idea_dict)

    # Persistencia Evaluacion
    nueva_eval = models.Evaluacion(
        idea_id=idea_id,
        modelo_ia=evaluacion_ia.modelo_ia,
        # mode='json' convierte el Enum Semaforo a string automáticamente para SQLite
        resultado=evaluacion_ia.evaluacion.model_dump(mode='json')
    )
    db.add(nueva_eval)
    db.flush()

    # Persistencia Trazabilidad del Prompt (4.4): prompt/respuesta reales.
    nuevo_log = models.PromptLog(
        evaluacion_id=nueva_eval.id,
        prompt=evaluacion_ia.prompt,
        respuesta_cruda=evaluacion_ia.respuesta_cruda,
        modelo_ia=evaluacion_ia.modelo_ia,
    )
    db.add(nuevo_log)
    db.commit()
    db.refresh(nueva_eval)

    return nueva_eval

def generar_comparacion(db: Session, idea_ids: list[str]) -> schemas.Comparacion:
    ideas_comp = []
    for idea_id in idea_ids:
        idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
        if idea and idea.evaluaciones:
            ultima_eval = idea.evaluaciones[-1]
            ideas_comp.append(schemas.IdeaComparacion(
                idea_id=idea.id,
                nombre=idea.nombre,
                semaforo=ultima_eval.resultado["semaforo"],
                criterios_evaluados=ultima_eval.resultado["criterios_evaluados"]
            ))

    return schemas.Comparacion(
        criterios=["problema", "mercado", "cliente", "diferenciacion", "riesgos", "monetizacion", "factibilidad"],
        ideas=ideas_comp
    )
