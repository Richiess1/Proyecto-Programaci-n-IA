from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 4.1 Idea
class IdeaBase(BaseModel):
    nombre: str
    descripcion: str
    problema: str
    publico_objetivo: str
    propuesta_valor: str
    contexto_inicial: Optional[str] = ""
    sector: Optional[str] = ""
    pais_mercado: Optional[str] = ""
    tipo_cliente: Optional[str] = ""
    canales: Optional[str] = ""
    recursos_disponibles: Optional[str] = ""
    restricciones: Optional[str] = ""
    competencia_conocida: Optional[str] = ""

class IdeaCreate(IdeaBase):
    pass

class Idea(IdeaBase):
    id: str
    class Config:
        from_attributes = True

# 4.2 EvaluacionIA
class Foda(BaseModel):
    fortalezas: List[str]
    debilidades: List[str]
    oportunidades: List[str]
    amenazas: List[str]

class PlanValidacion(BaseModel):
    tipo: str
    descripcion: str
    metrica: str

class CriteriosEvaluados(BaseModel):
    problema: str
    mercado: str
    cliente: str
    diferenciacion: str
    riesgos: str
    monetizacion: str
    factibilidad: str

class EvaluacionIA(BaseModel):
    semaforo: str
    justificacion_semaforo: str
    diagnostico: str
    foda: Foda
    supuestos_criticos: List[str]
    riesgos: List[str]
    propuesta_valor_mejorada: str
    preguntas_aclaracion: List[str]
    plan_validacion: List[PlanValidacion]
    criterios_evaluados: CriteriosEvaluados

# 4.3 Evaluacion
class Evaluacion(BaseModel):
    id: str
    idea_id: str
    version: int
    fecha: datetime
    modelo_ia: str
    estado: str
    resultado: EvaluacionIA
    class Config:
        from_attributes = True

class EstadoUpdate(BaseModel):
    estado: str

# 4.5 Comparacion
class IdeaComparacion(BaseModel):
    idea_id: str
    nombre: str
    semaforo: str
    criterios_evaluados: CriteriosEvaluados

class ComparacionReq(BaseModel):
    idea_ids: List[str]

class Comparacion(BaseModel):
    criterios: List[str]
    ideas: List[IdeaComparacion]

# 4.6 Error
class ErrorDetail(BaseModel):
    codigo: str
    mensaje: str

class ErrorResponse(BaseModel):
    error: ErrorDetail