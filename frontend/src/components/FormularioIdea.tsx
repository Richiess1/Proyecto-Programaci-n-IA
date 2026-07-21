import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../services/apiClient'

export default function FormularioIdea() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    problema: '',
    publico_objetivo: '',
    propuesta_valor: '',
    contexto_inicial: '',
    sector: '',
    pais_mercado: '',
    tipo_cliente: '',
    canales: '',
    recursos_disponibles: '',
    restricciones: '',
    competencia_conocida: ''
  })
  
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setErrorMsg('') // Clear error on edit
  }

  const handleGuardarSinEvaluar = async () => {
    try {
      setIsSaving(true)
      setErrorMsg('')
      await apiClient.crearIdea(formData)
      navigate('/')
    } catch (error: any) {
      setErrorMsg(error.mensaje || 'Error al guardar la idea.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleGuardarYEvaluar = async () => {
    if (!formData.nombre || !formData.descripcion || !formData.problema || !formData.publico_objetivo || !formData.propuesta_valor) {
      setErrorMsg('Por favor, completa los 5 campos obligatorios antes de evaluar.')
      return
    }

    try {
      setIsEvaluating(true)
      setErrorMsg('')
      
      // 1. Guardar la idea primero
      const ideaGuardada = await apiClient.crearIdea(formData)
      
      // 2. Enviar a evaluar
      await apiClient.evaluarIdea(ideaGuardada.id)
      
      // 3. Redirigir a la vista de detalle
      navigate(`/ideas/${ideaGuardada.id}`)
    } catch (error: any) {
      setErrorMsg(error.mensaje || 'Hubo un error al guardar o evaluar la idea.')
    } finally {
      setIsEvaluating(false)
    }
  }

  const inputClass = "w-full bg-white border border-[#D2D6DC] rounded-sm p-3 text-[13px] text-[#10161F] placeholder-[#7A828E] focus:outline-none focus:border-[#2454C7] resize-y"
  const labelClass = "block text-[11px] font-bold text-[#5B6472] mb-1.5 uppercase tracking-wide"

  return (
    <div className="w-full h-full max-w-6xl mx-auto px-10 py-8 relative flex flex-col">
      {/* Loader Overlay */}
      {isEvaluating && (
        <div className="absolute inset-0 bg-[#EDEFF2]/80 z-50 flex flex-col items-center justify-center rounded-lg">
          <div className="w-12 h-12 border-4 border-[#2454C7] border-t-transparent rounded-full animate-spin mb-4"></div>
          <h3 className="text-xl font-bold text-[#10161F]" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>Evaluando con IA...</h3>
          <p className="text-[#5B6472] mt-2">Esto puede tomar de 10 a 20 segundos.</p>
        </div>
      )}

      {/* Header con título y botones */}
      <div className="flex justify-between items-center mb-6 flex-shrink-0">
        <h1 className="text-2xl font-bold text-[#10161F] tracking-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
          Registrar nueva idea
        </h1>
        
        <div className="flex gap-3">
          <button 
            onClick={handleGuardarSinEvaluar}
            disabled={isSaving || isEvaluating}
            className="bg-[#F3F4F6] text-[#10161F] text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#E2E4E8] transition-colors border border-[#D2D6DC] disabled:opacity-50"
          >
            {isSaving ? 'Guardando...' : 'Guardar sin evaluar'}
          </button>
          <button 
            onClick={handleGuardarYEvaluar}
            disabled={isSaving || isEvaluating}
            className="bg-[#2454C7] text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#1a3fa0] transition-colors disabled:opacity-50"
          >
            Guardar y evaluar
          </button>
        </div>
      </div>

      {/* Mensaje de error global */}
      {errorMsg && (
        <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex-shrink-0">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-red-500">⚠️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700 font-medium">
                {errorMsg}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Formulario en 2 columnas */}
      <form className="grid grid-cols-1 lg:grid-cols-2 gap-10 flex-1 min-h-0" onSubmit={(e) => e.preventDefault()}>
        
        {/* Columna Izquierda: Obligatorios */}
        <div className="bg-white flex flex-col h-full border border-[#D2D6DC] border-t-[3px] border-t-[#2454C7] p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-5">
            <h2 className="text-base font-bold text-[#10161F]">Información básica</h2>
            <span className="text-[10px] font-bold bg-[#DCEFE0] text-[#1F6B3E] px-2 py-0.5 rounded-sm tracking-wide uppercase">OBLIGATORIO</span>
          </div>
          
          <div className="space-y-4 flex-1">
            <div>
              <label className={labelClass}>Nombre</label>
              <input 
                type="text" 
                name="nombre" 
                value={formData.nombre} 
                onChange={handleChange}
                placeholder="Nombre de la idea"
                className={inputClass}
                required
              />
            </div>
            
            <div>
              <label className={labelClass}>Descripción</label>
              <textarea 
                name="descripcion" 
                value={formData.descripcion} 
                onChange={handleChange}
                rows={2}
                placeholder="Resumen breve de la idea"
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Problema</label>
              <textarea 
                name="problema" 
                value={formData.problema} 
                onChange={handleChange}
                rows={2}
                placeholder="¿Qué problema resuelve?"
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Público objetivo</label>
              <textarea 
                name="publico_objetivo" 
                value={formData.publico_objetivo} 
                onChange={handleChange}
                rows={2}
                placeholder="¿Quién es el cliente o usuario?"
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Propuesta de valor</label>
              <textarea 
                name="propuesta_valor" 
                value={formData.propuesta_valor} 
                onChange={handleChange}
                rows={2}
                placeholder="¿Por qué te elegirían a ti?"
                className={inputClass}
                required
              />
            </div>
          </div>
        </div>

        {/* Columna Derecha: Opcionales */}
        <div className="bg-white flex flex-col h-full border border-[#D2D6DC] border-t-[3px] border-t-[#D2D6DC] p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-5">
            <h2 className="text-base font-bold text-[#10161F]">Datos complementarios</h2>
            <span className="text-[10px] font-bold bg-[#E2E4E8] text-[#5B6472] px-2 py-0.5 rounded-sm tracking-wide uppercase border border-[#D2D6DC]">OPCIONAL</span>
          </div>
          
          <div className="space-y-4 flex-1">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Contexto inicial</label>
                <textarea 
                  name="contexto_inicial" 
                  value={formData.contexto_inicial} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Origen de la idea"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Sector</label>
                <textarea 
                  name="sector" 
                  value={formData.sector} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Ej. Fintech, retail, salud"
                  className={inputClass}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>País / Mercado</label>
                <textarea 
                  name="pais_mercado" 
                  value={formData.pais_mercado} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Ej. Chile"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Tipo de cliente</label>
                <textarea 
                  name="tipo_cliente" 
                  value={formData.tipo_cliente} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Ej. B2C, B2B, B2G"
                  className={inputClass}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Canales</label>
                <textarea 
                  name="canales" 
                  value={formData.canales} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Cómo se llega al cliente"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Recursos disponibles</label>
                <textarea 
                  name="recursos_disponibles" 
                  value={formData.recursos_disponibles} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Equipo, capital, activos"
                  className={inputClass}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Restricciones</label>
                <textarea 
                  name="restricciones" 
                  value={formData.restricciones} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Regulaciones, límites conocidos"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Competencia conocida</label>
                <textarea 
                  name="competencia_conocida" 
                  value={formData.competencia_conocida} 
                  onChange={handleChange}
                  rows={2}
                  placeholder="Alternativas existentes"
                  className={inputClass}
                />
              </div>
            </div>
            
          </div>
        </div>

      </form>
    </div>
  )
}
