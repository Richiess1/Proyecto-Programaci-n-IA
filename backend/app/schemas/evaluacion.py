from __future__ import annotations
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from dataclasses import dataclass

# --- Contratos base (lo que ya tenías) ---

class Semaforo(str, Enum):
    """Estados posibles del semáforo (contrato 4.2)."""
    VERDE = "verde"
    AMARILLO = "amarillo"
    ROJO = "rojo"

class Foda(BaseModel):
    fortalezas: list[str]
    debilidades: list[str]
    oportunidades: list[str]
    amenazas: list[str]

class PasoValidacion(BaseModel):
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

    semaforo: Semaforo
    justificacion_semaforo: str
    diagnostico: str
    foda: Foda
    supuestos_criticos: list[str]
    riesgos: list[str]
    propuesta_valor_mejorada: str
    preguntas_aclaracion: list[str] = Field(default_factory=list)
    plan_validacion: list[PasoValidacion]
    criterios_evaluados: CriteriosEvaluados

class Idea(BaseModel):
    """Entrada del usuario (contrato 4.1).

    Cada campo tiene un `max_length`: acota el tamaño del prompt y cierra el abuso
    de costo (pegar textos gigantes para inflar el consumo de tokens). El límite se
    aplica al crear la idea, así nunca se persiste ni se manda al modelo algo fuera
    de rango.
    """
    id: str | None = None

    # Mínimos obligatorios antes de evaluar (RNF-04).
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1, max_length=3000)
    problema: str = Field(min_length=1, max_length=3000)
    publico_objetivo: str = Field(min_length=1, max_length=1500)
    propuesta_valor: str = Field(min_length=1, max_length=3000)

    # El resto puede ir vacío.
    contexto_inicial: str = Field(default="", max_length=3000)
    sector: str = Field(default="", max_length=200)
    pais_mercado: str = Field(default="", max_length=200)
    tipo_cliente: str = Field(default="", max_length=500)
    canales: str = Field(default="", max_length=1000)
    recursos_disponibles: str = Field(default="", max_length=2000)
    restricciones: str = Field(default="", max_length=2000)
    competencia_conocida: str = Field(default="", max_length=2000)

# --- Nuevos Contratos para la Base de Datos y la API ---

# Contrato 4.3 Evaluacion
class Evaluacion(BaseModel):
    id: str
    idea_id: str
    version: int
    fecha: datetime
    modelo_ia: str
    estado: str
    resultado: EvaluacionIA
    
    model_config = ConfigDict(from_attributes=True)

class EstadoUpdate(BaseModel):
    estado: str

# Contrato 4.5 Comparacion
class IdeaComparacion(BaseModel):
    idea_id: str
    nombre: str
    semaforo: Semaforo
    criterios_evaluados: CriteriosEvaluados

class ComparacionReq(BaseModel):
    # Tope de ideas por comparación: evita lotes gigantes que sobrecarguen la consulta.
    idea_ids: list[str] = Field(min_length=1, max_length=20)

class Comparacion(BaseModel):
    criterios: list[str]
    ideas: list[IdeaComparacion]

# Contrato 4.6 Error
class ErrorDetail(BaseModel):
    codigo: str
    mensaje: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

@dataclass(frozen=True)
class ResultadoMotorIA:
    """Retorno interno de evaluar_idea (sección 6, contrato v1.2).

    No es un shape de la API (4.x); es lo que el motor pasa al backend, que lo
    descompone:
      - evaluacion    -> campo `resultado` de Evaluacion (4.3)
      - modelo_ia     -> `modelo_ia` de Evaluacion (4.3) y de PromptLog (4.4)
      - prompt        -> `prompt` de PromptLog (4.4)
      - respuesta_cruda -> `respuesta_cruda` de PromptLog (4.4)
    """
    evaluacion: EvaluacionIA
    prompt: str
    respuesta_cruda: str
    modelo_ia: str
    # Consumo real reportado por el proveedor (para medir y controlar costos).
    tokens_prompt: int = 0
    tokens_completion: int = 0
    tokens_cache_hit: int = 0