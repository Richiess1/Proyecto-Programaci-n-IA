from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    problema = Column(String, nullable=False)
    publico_objetivo = Column(String, nullable=False)
    propuesta_valor = Column(String, nullable=False)
    contexto_inicial = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    pais_mercado = Column(String, nullable=True)
    tipo_cliente = Column(String, nullable=True)
    canales = Column(String, nullable=True)
    recursos_disponibles = Column(String, nullable=True)
    restricciones = Column(String, nullable=True)
    competencia_conocida = Column(String, nullable=True)

    evaluaciones = relationship("Evaluacion", back_populates="idea")

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(String, primary_key=True, default=generate_uuid)
    idea_id = Column(String, ForeignKey("ideas.id"))
    version = Column(Integer, default=1)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modelo_ia = Column(String)
    estado = Column(String, default="pendiente")
    resultado = Column(JSON)
    # Hash del contenido evaluado: permite reutilizar una evaluación ya hecha
    # para la misma idea sin re-gastar tokens (deduplicación).
    idea_hash = Column(String, index=True, nullable=True)

    idea = relationship("Idea", back_populates="evaluaciones")
    prompt_logs = relationship("PromptLog", back_populates="evaluacion")

class PromptLog(Base):
    __tablename__ = "prompt_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    evaluacion_id = Column(String, ForeignKey("evaluaciones.id"))
    prompt = Column(String)
    respuesta_cruda = Column(String)
    modelo_ia = Column(String)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Consumo real del proveedor, para monitorear costos (nullable: PromptLogs
    # viejos no lo tienen).
    tokens_prompt = Column(Integer, nullable=True)
    tokens_completion = Column(Integer, nullable=True)
    tokens_cache_hit = Column(Integer, nullable=True)

    evaluacion = relationship("Evaluacion", back_populates="prompt_logs")