const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Helper genérico para peticiones que maneja los 2 formatos de error
async function request(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      throw { mensaje: "Error inesperado en el servidor", detail: "El servidor no devolvió JSON válido" };
    }
    
    // Formato de error de negocio/IA
    if (errorData.error && errorData.error.codigo) {
      throw errorData.error; // { codigo: '...', mensaje: '...' }
    }
    
    // Formato de error estándar de FastAPI
    if (errorData.detail) {
      const msg = Array.isArray(errorData.detail)
        ? errorData.detail.map((err) => err.msg).join(", ")
        : errorData.detail;
      throw { mensaje: msg, detail: errorData.detail };
    }
    
    throw { mensaje: errorData.message || "Error desconocido" };
  }

  return response.json();
}

export const apiClient = {
  crearIdea: (ideaData) => {
    return request("/ideas", {
      method: "POST",
      body: JSON.stringify(ideaData),
    });
  },
  
  evaluarIdea: (ideaId) => {
    return request(`/ideas/${ideaId}/evaluar`, {
      method: "POST",
    });
  },
  
  obtenerIdeas: () => request("/ideas"),
  
  obtenerIdea: (ideaId) => request(`/ideas/${ideaId}`),
  
  obtenerEvaluaciones: (ideaId) => request(`/ideas/${ideaId}/evaluaciones`),
  
  cambiarEstadoEvaluacion: (evaluacionId, estado) => {
    return request(`/evaluaciones/${evaluacionId}/estado`, {
      method: "PATCH",
      body: JSON.stringify({ estado })
    });
  },
  
  compararIdeas: (ideaIds) => {
    return request("/comparar", {
      method: "POST",
      body: JSON.stringify({ idea_ids: ideaIds })
    });
  }
};
