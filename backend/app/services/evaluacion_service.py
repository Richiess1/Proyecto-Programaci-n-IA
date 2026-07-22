import hashlib
import json

from sqlalchemy.orm import Session
from app.db import models
from app.schemas import evaluacion as schemas  # <-- Cambio de import
from app.ia.motor_ia import evaluar_idea
from app.ia.prompts import PROMPT_VERSION
from app.core.config import settings

# Campos de la Idea que alimentan el prompt: el hash se calcula sobre ellos para
# detectar si ya evaluamos exactamente el mismo contenido.
_CAMPOS_CONTENIDO = [
    "nombre", "descripcion", "problema", "publico_objetivo", "propuesta_valor",
    "contexto_inicial", "sector", "pais_mercado", "tipo_cliente", "canales",
    "recursos_disponibles", "restricciones", "competencia_conocida",
]


def _hash_idea(idea_dict: dict, modelo_ia: str) -> str:
    """Hash estable del contenido + modelo + versión del prompt.

    Incluye el modelo y la versión del prompt porque una misma idea evaluada con
    otro modelo o con otro prompt es un resultado distinto: así, al cambiar el
    prompt, la evaluación se rehace en vez de devolver la cacheada."""
    contenido = {c: str(idea_dict.get(c, "") or "") for c in _CAMPOS_CONTENIDO}
    contenido["__modelo__"] = modelo_ia
    contenido["__prompt__"] = PROMPT_VERSION
    canonico = json.dumps(contenido, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def procesar_evaluacion(db: Session, idea_id: str) -> models.Evaluacion:
    idea_db = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea_db:
        raise ValueError("Idea no encontrada")

    # Convierte a dict para enviarlo al motor
    idea_dict = {c.name: getattr(idea_db, c.name) for c in idea_db.__table__.columns}

    # Deduplicación por CONTENIDO: la huella depende del contenido + modelo +
    # versión del prompt, no de la idea_id. Así, escribir la misma idea (aunque
    # sea un registro nuevo) reutiliza el resultado y NO gasta tokens.
    huella = _hash_idea(idea_dict, settings.IA_MODELO)

    # 1) ¿Esta misma idea ya tiene una evaluación con esta huella? Devolvemos esa.
    existente = (
        db.query(models.Evaluacion)
        .filter(
            models.Evaluacion.idea_id == idea_id,
            models.Evaluacion.idea_hash == huella,
        )
        .order_by(models.Evaluacion.fecha.desc())
        .first()
    )
    if existente:
        return existente

    # 2) ¿Otra idea con contenido idéntico? Copiamos su resultado a una evaluación
    # nueva para esta idea, sin volver a llamar a la IA.
    cacheada = (
        db.query(models.Evaluacion)
        .filter(models.Evaluacion.idea_hash == huella)
        .order_by(models.Evaluacion.fecha.desc())
        .first()
    )
    if cacheada:
        copia = models.Evaluacion(
            idea_id=idea_id,
            modelo_ia=cacheada.modelo_ia,
            idea_hash=huella,
            resultado=cacheada.resultado,
        )
        db.add(copia)
        db.flush()
        db.add(models.PromptLog(
            evaluacion_id=copia.id,
            prompt=f"[reutilizado de evaluación {cacheada.id}]",
            respuesta_cruda="[reutilizado de caché: sin llamada a la IA]",
            modelo_ia=cacheada.modelo_ia,
            tokens_prompt=0,
            tokens_completion=0,
            tokens_cache_hit=0,
        ))
        db.commit()
        db.refresh(copia)
        return copia

    # 3) No hay nada cacheado: llamamos al motor de IA (puede cortar antes con
    # EntradaIncompletaError, sin gastar tokens, si la idea está incompleta).
    evaluacion_ia = evaluar_idea(idea_dict)

    # Persistencia Evaluacion
    nueva_eval = models.Evaluacion(
        idea_id=idea_id,
        modelo_ia=evaluacion_ia.modelo_ia,
        idea_hash=huella,
        # mode='json' convierte el Enum Semaforo a string automáticamente para SQLite
        resultado=evaluacion_ia.evaluacion.model_dump(mode='json')
    )
    db.add(nueva_eval)
    db.flush()

    # Persistencia Trazabilidad del Prompt (4.4): prompt/respuesta reales + consumo.
    nuevo_log = models.PromptLog(
        evaluacion_id=nueva_eval.id,
        prompt=evaluacion_ia.prompt,
        respuesta_cruda=evaluacion_ia.respuesta_cruda,
        modelo_ia=evaluacion_ia.modelo_ia,
        tokens_prompt=evaluacion_ia.tokens_prompt,
        tokens_completion=evaluacion_ia.tokens_completion,
        tokens_cache_hit=evaluacion_ia.tokens_cache_hit,
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
