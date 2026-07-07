from __future__ import annotations

from app.schemas.evaluacion import (
    CriteriosEvaluados,
    EvaluacionIA,
    Foda,
    PasoValidacion,
    Semaforo,
)


def evaluar_idea(idea: dict) -> EvaluacionIA:
    """Evalúa una Idea (4.1) y devuelve una EvaluacionIA (4.2).

    Etapa 1: ignora `idea` y devuelve un mock válido para desbloquear al
    backend. La firma se mantiene en la etapa 2, cuando por dentro se llame
    al proveedor de IA real, así la integración no rompe nada.
    """
    # TODO(etapa 2): construir el prompt, llamar al proveedor, parsear y validar
    # la respuesta; lanzar las excepciones tipadas de app.ia.excepciones según el
    # fallo. Hasta entonces se ignora `idea`.
    _ = idea

    return EvaluacionIA(
        semaforo=Semaforo.AMARILLO,
        justificacion_semaforo=(
            "El problema es real y hay demanda, pero la propuesta de valor "
            "todavía no se diferencia con claridad de los intermediarios actuales "
            "y faltan supuestos validados sobre la disposición a pagar."
        ),
        diagnostico=(
            "La idea ataca una fricción concreta entre productores locales y "
            "restaurantes, con un mercado accesible en el corto plazo. El mayor "
            "vacío está en la monetización y en cómo se sostiene la ventaja una vez "
            "que un competidor con más capital copie el modelo."
        ),
        foda=Foda(
            fortalezas=[
                "Conocimiento directo del dolor del cliente que compra a productores.",
                "Modelo operable con un equipo pequeño en su fase inicial.",
            ],
            debilidades=[
                "Diferenciación débil frente a distribuidores ya establecidos.",
                "Dependencia de lograr masa crítica en ambos lados del mercado.",
            ],
            oportunidades=[
                "Tendencia de consumo hacia el producto local y trazable.",
                "Posibilidad de sumar logística como ingreso adicional.",
            ],
            amenazas=[
                "Entrada de un competidor con más capital y la misma propuesta.",
                "Estacionalidad de la oferta agrícola que afecta el inventario.",
            ],
        ),
        supuestos_criticos=[
            "Los restaurantes están dispuestos a pagar una comisión por pedido.",
            "Hay suficientes productores dispuestos a vender por el canal.",
        ],
        riesgos=[
            "Que el volumen inicial no cubra los costos logísticos.",
            "Que un lado del mercado crezca sin el otro (desbalance de oferta y demanda).",
        ],
        propuesta_valor_mejorada=(
            "Marketplace que garantiza a los restaurantes producto local trazable "
            "con entrega en 24 h, y a los productores un canal de venta con pago "
            "asegurado; la ventaja se sostiene con la relación directa y los datos "
            "de demanda, no solo con el precio."
        ),
        preguntas_aclaracion=[
            "¿Qué comisión o tarifa piensa cobrar y a quién?",
            "¿Cuenta con logística propia o la terceriza?",
        ],
        plan_validacion=[
            PasoValidacion(
                tipo="entrevista",
                descripcion="Entrevistar a 10 restaurantes sobre su compra actual.",
                metrica="Nº de restaurantes que confirman interés y comisión aceptable.",
            ),
            PasoValidacion(
                tipo="piloto",
                descripcion="Operar manualmente 2 semanas con 3 productores y 5 restaurantes.",
                metrica="Pedidos completados y margen por pedido.",
            ),
        ],
        criterios_evaluados=CriteriosEvaluados(
            problema="Claro y validado: fricción real en la compra a productores.",
            mercado="Accesible y con tendencia favorable, aún por dimensionar.",
            cliente="Bien identificado (restaurantes); falta perfilar al productor.",
            diferenciacion="Débil todavía; hay que sostenerla más allá del precio.",
            riesgos="Moderados, concentrados en logística y balance del marketplace.",
            monetizacion="Sin definir; es el punto más urgente a cerrar.",
            factibilidad="Alta para un piloto manual; escalar requiere inversión.",
        ),
    )