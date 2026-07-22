import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Sidebar from '../../components/Sidebar'
import ChipSemaforo from '../../components/ChipSemaforo'
import { getIdea, getEvaluaciones, evaluarIdea, cambiarEstado } from '../../services/apiClient'

const colorSemaforo: Record<string, string> = {
  verde: '#2E7D4F',
  amarillo: '#B07A17',
  rojo: '#B23A3A',
}

interface Idea {
  id: string
  nombre: string
  descripcion: string
  problema: string
  publico_objetivo: string
  propuesta_valor: string
  sector?: string
  pais_mercado?: string
}

interface EvaluacionIA {
  semaforo: 'verde' | 'amarillo' | 'rojo'
  justificacion_semaforo: string
  diagnostico: string
  foda: {
    fortalezas: string[]
    debilidades: string[]
    oportunidades: string[]
    amenazas: string[]
  }
  supuestos_criticos: string[]
  riesgos: string[]
  propuesta_valor_mejorada: string
  preguntas_aclaracion: string[]
  plan_validacion: { tipo: string; descripcion: string; metrica: string }[]
  criterios_evaluados: Record<string, string>
}

interface Evaluacion {
  id: string
  idea_id: string
  version: number
  fecha: string
  modelo_ia: string
  estado: string
  resultado: EvaluacionIA
}

const ESTADOS = ['pendiente', 'aceptado', 'descartado']

export default function Detalle() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [idea, setIdea] = useState<Idea | null>(null)
  const [evaluaciones, setEvaluaciones] = useState<Evaluacion[]>([])
  const [cargando, setCargando] = useState(true)
  const [evaluando, setEvaluando] = useState(false)
  const [error, setError] = useState('')
  const [cambiandoEstado, setCambiandoEstado] = useState(false)

  const cargarDatos = useCallback(async () => {
    if (!id) return
    try {
      setCargando(true)
      setError('')
      const [ideaData, evalsData] = await Promise.all([
        getIdea(id),
        getEvaluaciones(id),
      ])
      setIdea(ideaData)
      setEvaluaciones(evalsData)
    } catch (e: any) {
      setError(e.message || 'Error al cargar la idea')
    } finally {
      setCargando(false)
    }
  }, [id])

  useEffect(() => {
    cargarDatos()
  }, [cargarDatos])

  const ultimaEvaluacion = evaluaciones[evaluaciones.length - 1]

  const handleEvaluar = async () => {
    if (!id) return
    try {
      setEvaluando(true)
      setError('')
      await evaluarIdea(id)
      await cargarDatos()
    } catch (e: any) {
      setError(e.message || 'Hubo un error al evaluar la idea.')
    } finally {
      setEvaluando(false)
    }
  }

  const handleCambiarEstado = async (estado: string) => {
    if (!ultimaEvaluacion) return
    try {
      setCambiandoEstado(true)
      await cambiarEstado(ultimaEvaluacion.id, estado)
      await cargarDatos()
    } catch (e: any) {
      setError(e.message || 'Error al cambiar el estado.')
    } finally {
      setCambiandoEstado(false)
    }
  }

  if (cargando) {
    return (
      <div className="min-h-screen bg-[#EDEFF2] flex">
        <Sidebar />
        <main className="ml-52 flex-1 px-10 py-8">
          <p className="text-sm text-[#5B6472] text-center mt-10">Cargando idea...</p>
        </main>
      </div>
    )
  }

  if (error && !idea) {
    return (
      <div className="min-h-screen bg-[#EDEFF2] flex">
        <Sidebar />
        <main className="ml-52 flex-1 px-10 py-8">
          <div className="bg-[#F5D6D3] border border-[#B23A3A] text-[#8B2E24] text-sm px-4 py-3 rounded-sm">
            {error}
          </div>
          <button onClick={() => navigate('/')} className="mt-4 text-sm text-[#2454C7] hover:underline">
            ← Volver al listado
          </button>
        </main>
      </div>
    )
  }

  if (!idea) return null

  const resultado = ultimaEvaluacion?.resultado

  return (
    <div className="min-h-screen bg-[#EDEFF2] flex">
      <Sidebar />
      <main className="ml-52 flex-1 px-10 py-8 max-w-5xl">
        <button onClick={() => navigate('/')} className="text-sm text-[#2454C7] hover:underline mb-4">
          ← Volver al listado
        </button>

        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-[#10161F] tracking-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                {idea.nombre}
              </h1>
              {resultado && <ChipSemaforo semaforo={resultado.semaforo} />}
            </div>
            {idea.sector && <p className="text-[11px] text-[#5B6472] tracking-wide uppercase mt-1">{idea.sector}</p>}
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-[#F5D6D3] border border-[#B23A3A] text-[#8B2E24] text-sm px-4 py-3 rounded-sm">
            {error}
          </div>
        )}

        {evaluando && (
          <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-6 mb-6 flex flex-col items-center">
            <div className="w-10 h-10 border-4 border-[#2454C7] border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm text-[#5B6472]">Esto puede tomar de 10 a 20 segundos.</p>
          </div>
        )}

        {/* Ficha de la idea */}
        <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 mb-6 shadow-sm">
          <h2 className="text-base font-bold text-[#10161F] mb-3">Ficha de la idea</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div className="sm:col-span-2">
              <p className="text-[11px] font-bold text-[#5B6472] uppercase tracking-wide mb-1">Descripción</p>
              <p className="text-[#232B36]">{idea.descripcion}</p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#5B6472] uppercase tracking-wide mb-1">Problema</p>
              <p className="text-[#232B36]">{idea.problema}</p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#5B6472] uppercase tracking-wide mb-1">Público objetivo</p>
              <p className="text-[#232B36]">{idea.publico_objetivo}</p>
            </div>
            <div className="sm:col-span-2">
              <p className="text-[11px] font-bold text-[#5B6472] uppercase tracking-wide mb-1">Propuesta de valor</p>
              <p className="text-[#232B36]">{idea.propuesta_valor}</p>
            </div>
          </div>
        </div>

        {!resultado && !evaluando && (
          <p className="text-sm text-[#5B6472] text-center mt-10">
            Esta idea todavía no tiene evaluación. Presioná "Evaluar con IA" para generar una.
          </p>
        )}

        {resultado && (
          <div className="flex flex-col gap-6">
            {/* Semáforo + diagnóstico */}
            <div
              className="bg-white border border-[#D2D6DC] border-t-[3px] rounded-sm px-5 py-5 shadow-sm"
              style={{ borderTopColor: colorSemaforo[resultado.semaforo] }}
            >
              <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
                <h2 className="text-base font-bold text-[#10161F]">Diagnóstico</h2>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-[#7A828E]">
                    V{ultimaEvaluacion.version} · {new Date(ultimaEvaluacion.fecha).toLocaleDateString('es-SV', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}
                  </span>
                  <select
                    value={ultimaEvaluacion.estado}
                    disabled={cambiandoEstado}
                    onChange={(e) => handleCambiarEstado(e.target.value)}
                    className="text-[11px] font-medium bg-[#E2E4E8] text-[#5B6472] px-2 py-1 rounded-sm uppercase tracking-wide border border-[#D2D6DC] disabled:opacity-50"
                  >
                    {ESTADOS.map((e) => (
                      <option key={e} value={e}>{e}</option>
                    ))}
                  </select>
                </div>
              </div>
              <p className="text-sm text-[#232B36] mb-2">{resultado.justificacion_semaforo}</p>
              <p className="text-sm text-[#232B36] leading-relaxed">{resultado.diagnostico}</p>
            </div>

            {/* FODA */}
            <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 shadow-sm">
              <h2 className="text-base font-bold text-[#10161F] mb-4">FODA</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {([
                  ['Fortalezas', resultado.foda.fortalezas, '#DCEFE0', '#1F6B3E'],
                  ['Debilidades', resultado.foda.debilidades, '#F5D6D3', '#8B2E24'],
                  ['Oportunidades', resultado.foda.oportunidades, '#DCEFE0', '#1F6B3E'],
                  ['Amenazas', resultado.foda.amenazas, '#F5D6D3', '#8B2E24'],
                ] as [string, string[], string, string][]).map(([titulo, items]) => (
                  <div key={titulo}>
                    <p className="text-[11px] font-bold text-[#5B6472] uppercase tracking-wide mb-2">{titulo}</p>
                    <ul className="list-disc list-inside text-sm text-[#232B36] space-y-1">
                      {items.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Riesgos y supuestos */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 shadow-sm">
                <h2 className="text-base font-bold text-[#10161F] mb-3">Riesgos</h2>
                <ul className="list-disc list-inside text-sm text-[#232B36] space-y-1">
                  {resultado.riesgos.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
              <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 shadow-sm">
                <h2 className="text-base font-bold text-[#10161F] mb-3">Supuestos críticos</h2>
                <ul className="list-disc list-inside text-sm text-[#232B36] space-y-1">
                  {resultado.supuestos_criticos.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            </div>

            {/* Propuesta de valor mejorada */}
            <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 shadow-sm">
              <h2 className="text-base font-bold text-[#10161F] mb-3">Propuesta de valor mejorada</h2>
              <p className="text-sm text-[#232B36] leading-relaxed">{resultado.propuesta_valor_mejorada}</p>
            </div>

            {/* Preguntas de aclaración */}
            {resultado.preguntas_aclaracion.length > 0 && (
              <div className="bg-white border border-[#D2D6DC] border-l-4 border-l-[#B07A17] rounded-sm px-5 py-5 shadow-sm">
                <h2 className="text-base font-bold text-[#10161F] mb-3">Preguntas de aclaración</h2>
                <p className="text-xs text-[#5B6472] mb-2">Información que falta para una evaluación más sólida:</p>
                <ul className="list-disc list-inside text-sm text-[#232B36] space-y-1">
                  {resultado.preguntas_aclaracion.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            )}

            {/* Plan de validación */}
            <div className="bg-white border border-[#D2D6DC] rounded-sm px-5 py-5 shadow-sm">
              <h2 className="text-base font-bold text-[#10161F] mb-3">Plan de validación</h2>
              <div className="flex flex-col divide-y divide-[#EDEFF2]">
                {resultado.plan_validacion.map((paso, i) => (
                  <div key={i} className="py-3 grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <span className="text-[11px] font-bold text-[#2454C7] uppercase tracking-wide">{paso.tipo}</span>
                    <span className="text-sm text-[#232B36] sm:col-span-1">{paso.descripcion}</span>
                    <span className="text-sm text-[#5B6472]">{paso.metrica}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
