from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


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
    # extra="forbid": la IA no puede agregar campos fuera del contrato 4.2.
    model_config = ConfigDict(extra="forbid")

    semaforo: Semaforo
    justificacion_semaforo: str
    diagnostico: str
    foda: Foda
    supuestos_criticos: list[str]
    riesgos: list[str]
    propuesta_valor_mejorada: str
    preguntas_aclaracion: list[str] = Field(default_factory=list)  # puede venir vacío
    plan_validacion: list[PasoValidacion]
    criterios_evaluados: CriteriosEvaluados


class Idea(BaseModel):
    """Entrada del usuario (contrato 4.1)."""
    id: str | None = None

    # Mínimos obligatorios antes de evaluar (RNF-04).
    nombre: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    problema: str = Field(min_length=1)
    publico_objetivo: str = Field(min_length=1)
    propuesta_valor: str = Field(min_length=1)

    # El resto puede ir vacío.
    contexto_inicial: str = ""
    sector: str = ""
    pais_mercado: str = ""
    tipo_cliente: str = ""
    canales: str = ""
    recursos_disponibles: str = ""
    restricciones: str = ""
    competencia_conocida: str = ""