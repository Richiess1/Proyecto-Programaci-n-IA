import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Sidebar from '../../components/Sidebar'
import BannerSemaforo from '../../components/BannerSemaforo'
import ControlEstado from '../../components/ControlEstado'
import TarjetaFoda from '../../components/TarjetaFoda'
import HistorialVersiones from '../../components/HistorialVersiones'

import { apiClient } from '../../services/apiClient'

export default function Detalle() {
  const navigate = useNavigate()
  const { id } = useParams()
  
  const [idea, setIdea] = useState<any>(null)
  const [evaluaciones, setEvaluaciones] = useState<any[]>([])
  const [evaluacionActiva, setEvaluacionActiva] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      if (!id) return
      setLoading(true)
      try {
        const ideaData = await apiClient.obtenerIdea(id)
        setIdea(ideaData)
        
        const evalsData = await apiClient.obtenerEvaluaciones(id)
        setEvaluaciones(evalsData)
        
        // Tomar la evaluación más reciente (o la única que exista)
        if (evalsData.length > 0) {
          // Ordenar por versión descendente si es necesario, o simplemente tomar la primera
          const evalsSorted = [...evalsData].sort((a, b) => b.version - a.version)
          setEvaluacionActiva(evalsSorted[0])
        }
      } catch (err: any) {
        setError(err.mensaje || 'Error al cargar los datos')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleCambiarEstado = async (nuevoEstado: 'PENDIENTE' | 'ACEPTADO' | 'DESCARTADO') => {
    if (!evaluacionActiva) return
    try {
      const updated = await apiClient.cambiarEstadoEvaluacion(evaluacionActiva.id, nuevoEstado)
      setEvaluacionActiva(updated)
      // Actualizar en la lista también
      setEvaluaciones(prev => prev.map(ev => ev.id === updated.id ? updated : ev))
    } catch (err: any) {
      alert("Error al cambiar estado: " + err.mensaje)
    }
  }

  if (loading) {
    return <div className="h-screen flex items-center justify-center bg-[#EDEFF2]">Cargando...</div>
  }

  if (error || !idea) {
    return <div className="h-screen flex items-center justify-center bg-[#EDEFF2] text-red-500">{error || 'Idea no encontrada'}</div>
  }

  // Label UI helper
  const Label = ({ children }: { children: React.ReactNode }) => (
    <span className="block text-[10px] font-bold text-[#5B6472] mb-1 uppercase tracking-widest">{children}</span>
  )
  const Value = ({ children }: { children: React.ReactNode }) => (
    <p className="text-[13px] text-[#10161F] leading-relaxed break-words">
      {children || <span className="text-gray-400 italic">No especificado</span>}
    </p>
  )

  const CardTitle = ({ children }: { children: React.ReactNode }) => (
    <h3 className="text-sm font-bold text-[#10161F] mb-4">{children}</h3>
  )

  // Mapear criterios del objeto a array para el UI
  const criteriosArray = evaluacionActiva?.resultado?.criterios_evaluados 
    ? Object.entries(evaluacionActiva.resultado.criterios_evaluados).map(([key, value]: [string, any]) => {
        // Determinar color en base al string (puede venir en minúscula)
        const v = typeof value === 'string' ? value.toUpperCase() : 'MODERADO'
        let color = 'amarillo'
        if (v === 'FUERTE') color = 'verde'
        if (v === 'DÉBIL' || v === 'DEBIL' || v === 'BAJO') color = 'rojo'
        
        return {
          nombre: key.charAt(0).toUpperCase() + key.slice(1),
          evaluacion: v,
          color
        }
      })
    : []

  // Mapear historial
  const historialArray = evaluaciones.map(ev => {
    const sem = ev.resultado?.semaforo?.toLowerCase() || 'amarillo'
    return {
      version: ev.version,
      fecha: new Date(ev.fecha).toLocaleDateString(),
      color: sem === 'verde' ? 'verde' : sem === 'rojo' ? 'rojo' : 'amarillo'
    }
  })

  return (
    <div className="h-screen overflow-hidden bg-[#EDEFF2] flex">
      <Sidebar />
      <main className="ml-52 flex-1 h-screen overflow-y-auto">
        <div className="max-w-[1200px] mx-auto p-8">
          
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-4 mb-2">
              <button 
                onClick={() => navigate(-1)} 
                className="w-6 h-6 flex items-center justify-center bg-white border border-[#D2D6DC] text-[#5B6472] hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <h1 className="text-2xl font-bold text-[#10161F] leading-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                {idea.nombre}
              </h1>
              {idea.sector && (
                <span className="bg-[#E2E4E8] text-[#5B6472] text-[10px] font-bold uppercase tracking-widest px-2 py-1">
                  {idea.sector}
                </span>
              )}
            </div>
            <p className="text-[13px] text-[#5B6472] leading-relaxed">
              {idea.descripcion}
            </p>
          </div>

          {/* Grid Principal (70% - 30%) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Columna Izquierda (w-70%) */}
            <div className="lg:col-span-8 space-y-6">
              
              {/* Información Registrada */}
              <div className="bg-white p-6 border border-[#D2D6DC]">
                <CardTitle>Información registrada</CardTitle>
                <div className="grid grid-cols-2 gap-x-8 gap-y-6">
                  <div><Label>DESCRIPCIÓN</Label><Value>{idea.descripcion}</Value></div>
                  <div><Label>PROBLEMA</Label><Value>{idea.problema}</Value></div>
                  
                  <div><Label>PÚBLICO OBJETIVO</Label><Value>{idea.publico_objetivo}</Value></div>
                  <div><Label>PROPUESTA DE VALOR</Label><Value>{idea.propuesta_valor}</Value></div>
                  
                  <div><Label>CONTEXTO INICIAL</Label><Value>{idea.contexto_inicial}</Value></div>
                  <div><Label>PAÍS / MERCADO</Label><Value>{idea.pais_mercado}</Value></div>
                  
                  <div><Label>TIPO DE CLIENTE</Label><Value>{idea.tipo_cliente}</Value></div>
                  <div><Label>CANALES</Label><Value>{idea.canales}</Value></div>
                  
                  <div><Label>RECURSOS DISPONIBLES</Label><Value>{idea.recursos_disponibles}</Value></div>
                  <div><Label>RESTRICCIONES</Label><Value>{idea.restricciones}</Value></div>
                  
                  <div className="col-span-2"><Label>COMPETENCIA CONOCIDA</Label><Value>{idea.competencia_conocida}</Value></div>
                </div>
              </div>

              {evaluacionActiva && evaluacionActiva.resultado && (
                <>
                  {/* Preguntas de Aclaración */}
                  {evaluacionActiva.resultado.preguntas_aclaracion?.length > 0 && (
                    <div className="bg-white p-6 border border-[#D2D6DC]">
                      <CardTitle>Preguntas de aclaración</CardTitle>
                      <ul className="space-y-3">
                        {evaluacionActiva.resultado.preguntas_aclaracion.map((p: string, idx: number) => (
                          <li key={idx} className="text-[13px] text-[#2454C7] pb-3 border-b border-[#E2E4E8] last:border-0 last:pb-0">{p}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Diagnóstico */}
                  <div className="bg-white p-6 border border-[#D2D6DC]">
                    <CardTitle>Diagnóstico</CardTitle>
                    <p className="text-[13px] text-[#10161F] leading-relaxed">
                      {evaluacionActiva.resultado.diagnostico}
                    </p>
                  </div>

                  {/* FODA */}
                  {evaluacionActiva.resultado.foda && (
                    <TarjetaFoda foda={evaluacionActiva.resultado.foda} />
                  )}

                  {/* Supuestos Críticos y Riesgos */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-6 border border-[#D2D6DC]">
                      <CardTitle>Supuestos críticos</CardTitle>
                      <ul className="space-y-2">
                        {evaluacionActiva.resultado.supuestos_criticos?.map((s: string, i: number) => (
                          <li key={i} className="text-[13px] text-[#10161F] flex items-start"><span className="mr-2 mt-0.5">•</span><span className="leading-relaxed">{s}</span></li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-white p-6 border border-[#D2D6DC]">
                      <CardTitle>Riesgos</CardTitle>
                      <ul className="space-y-2">
                        {evaluacionActiva.resultado.riesgos?.map((r: string, i: number) => (
                          <li key={i} className="text-[13px] text-[#10161F] flex items-start"><span className="mr-2 mt-0.5">•</span><span className="leading-relaxed">{r}</span></li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Propuesta de Valor Original vs IA */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-[#F8F9FA] p-6 border border-[#D2D6DC]">
                      <h3 className="text-[10px] font-bold text-[#5B6472] uppercase tracking-widest mb-3">PROPUESTA DE VALOR ORIGINAL</h3>
                      <p className="text-[13px] text-[#10161F] leading-relaxed">{idea.propuesta_valor}</p>
                    </div>
                    {evaluacionActiva.resultado.propuesta_valor_mejorada && (
                      <div className="bg-white p-6 border border-[#D2D6DC] border-t-[3px] border-t-[#2454C7]">
                        <h3 className="text-[10px] font-bold text-[#2454C7] uppercase tracking-widest mb-3">PROPUESTA DE VALOR MEJORADA (IA)</h3>
                        <p className="text-[13px] text-[#10161F] leading-relaxed">{evaluacionActiva.resultado.propuesta_valor_mejorada}</p>
                      </div>
                    )}
                  </div>

                  {/* Plan de validación */}
                  {evaluacionActiva.resultado.plan_validacion?.length > 0 && (
                    <div className="bg-white p-6 border border-[#D2D6DC]">
                      <CardTitle>Plan de validación</CardTitle>
                      <div className="divide-y divide-[#E2E4E8]">
                        {evaluacionActiva.resultado.plan_validacion.map((plan: any, i: number) => (
                          <div key={i} className="grid grid-cols-12 py-3 gap-4 items-center">
                            <div className="col-span-3 text-[10px] font-bold text-[#5B6472] uppercase tracking-widest">{plan.tipo}</div>
                            <div className="col-span-5 text-[12px] text-[#10161F]">{plan.descripcion}</div>
                            <div className="col-span-4 text-[12px] text-[#5B6472]">{plan.metrica || plan.meta}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              
              {!evaluacionActiva && (
                <div className="bg-white p-6 border border-[#D2D6DC] text-center text-[#5B6472]">
                  Esta idea aún no ha sido evaluada o no se generó el resultado correctamente.
                </div>
              )}
            </div>

            {/* Columna Derecha (w-30%) */}
            <div className="lg:col-span-4">
              {evaluacionActiva?.resultado && (
                <BannerSemaforo 
                  semaforo={evaluacionActiva.resultado.semaforo?.toUpperCase() as any} 
                  resumen={evaluacionActiva.resultado.justificacion_semaforo} 
                />
              )}
              
              {evaluacionActiva && (
                <ControlEstado estadoActual={evaluacionActiva.estado.toUpperCase()} onCambiarEstado={handleCambiarEstado} />
              )}
              
              {/* Criterios Evaluados */}
              {criteriosArray.length > 0 && (
                <div className="bg-white p-4 border border-[#D2D6DC] mb-4">
                  <h3 className="text-[10px] font-bold text-[#5B6472] uppercase tracking-widest mb-4">CRITERIOS EVALUADOS</h3>
                  <div className="space-y-2">
                    {criteriosArray.map((crit, idx) => {
                      const tagBg = crit.color === 'verde' ? 'bg-[#EAF3EC] text-[#1F6B3E]' : crit.color === 'amarillo' ? 'bg-[#FEF7E0] text-[#B06000]' : 'bg-[#FCE8E6] text-[#A50E0E]'
                      return (
                        <div key={idx} className="flex justify-between items-center py-2 border-b border-[#E2E4E8] last:border-0 last:pb-0">
                          <span className="text-[12px] text-[#10161F]">{crit.nombre}</span>
                          <span className={`text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 ${tagBg}`}>
                            {crit.evaluacion}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
              
              <HistorialVersiones historial={historialArray as any} />
            </div>

          </div>
        </div>
      </main>
    </div>
  )
}