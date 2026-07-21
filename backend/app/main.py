from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import endpoints
from app.db.session import engine, Base
from app.db.migraciones import aplicar_migraciones
from app.ia.motor_ia import (
    EntradaIncompletaError,
    FormatoInesperado,
    LimiteTokensError,
    ProveedorIAError,
    RespuestaInvalidaIA,
)

Base.metadata.create_all(bind=engine)
aplicar_migraciones(engine)

app = FastAPI(title="Evaluador de Ideas API")

# CORS: permite que el front (dev) llame al backend desde otro origen. Los puertos
# cubren Vite (5173) y CRA (3000). Ajustar/ampliar cuando haya dominio de producción.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

# Mapeo de errores de la sección 4.6
def crear_respuesta_error(codigo: str, mensaje: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"codigo": codigo, "mensaje": mensaje}}
    )

@app.exception_handler(RespuestaInvalidaIA)
async def respuesta_invalida_handler(request: Request, exc: RespuestaInvalidaIA):
    return crear_respuesta_error("IA_RESPUESTA_INVALIDA", str(exc), 502)

@app.exception_handler(ProveedorIAError)
async def proveedor_ia_handler(request: Request, exc: ProveedorIAError):
    return crear_respuesta_error("IA_PROVEEDOR", str(exc), 503)

@app.exception_handler(LimiteTokensError)
async def tokens_handler(request: Request, exc: LimiteTokensError):
    return crear_respuesta_error("IA_LIMITE_TOKENS", str(exc), 429)

@app.exception_handler(FormatoInesperado)
async def formato_handler(request: Request, exc: FormatoInesperado):
    return crear_respuesta_error("FORMATO_INESPERADO", str(exc), 500)

@app.exception_handler(EntradaIncompletaError)
async def entrada_incompleta_handler(request: Request, exc: EntradaIncompletaError):
    # Rechazo local, sin gastar tokens: la idea no trae info suficiente.
    return crear_respuesta_error("ENTRADA_INCOMPLETA", str(exc), 422)
