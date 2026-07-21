const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── Utilidad de manejo de errores ──────────────────────────────
async function manejarRespuesta(res) {
  const data = await res.json()
  if (!res.ok) {
    // Formato A: errores de negocio/IA
    if (data.error?.codigo) throw new Error(data.error.mensaje)
    // Formato B: errores estándar de FastAPI
    if (data.detail) {
      const msg = Array.isArray(data.detail)
        ? data.detail.map((e) => e.msg).join(', ')
        : data.detail
      throw new Error(msg)
    }
    throw new Error('Error inesperado')
  }
  return data
}

// ── Ideas ───────────────────────────────────────────────────────
export async function getIdeas() {
  const res = await fetch(`${API}/ideas`)
  return manejarRespuesta(res)
}

export async function getIdea(id) {
  const res = await fetch(`${API}/ideas/${id}`)
  return manejarRespuesta(res)
}

export async function crearIdea(datos) {
  const res = await fetch(`${API}/ideas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  return manejarRespuesta(res)
}

// ── Evaluaciones ────────────────────────────────────────────────
export async function evaluarIdea(idea_id) {
  const res = await fetch(`${API}/ideas/${idea_id}/evaluar`, {
    method: 'POST',
  })
  return manejarRespuesta(res)
}

export async function getEvaluaciones(idea_id) {
  const res = await fetch(`${API}/ideas/${idea_id}/evaluaciones`)
  return manejarRespuesta(res)
}

export async function cambiarEstado(evaluacion_id, estado) {
  const res = await fetch(`${API}/evaluaciones/${evaluacion_id}/estado`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ estado }),
  })
  return manejarRespuesta(res)
}

// ── Comparación ─────────────────────────────────────────────────
export async function compararIdeas(idea_ids) {
  const res = await fetch(`${API}/comparar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idea_ids }),
  })
  return manejarRespuesta(res)
}