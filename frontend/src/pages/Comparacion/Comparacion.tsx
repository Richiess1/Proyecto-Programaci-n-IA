import { useState, useEffect } from 'react'
import ChipSemaforo from '../../components/ChipSemaforo'
import Sidebar from '../../components/Sidebar'
import { getIdeas, compararIdeas } from '../../services/apiClient'

const CRITERIOS = [
  { key: 'problema',       label: 'Problema' },
  { key: 'mercado',        label: 'Mercado' },
  { key: 'cliente',        label: 'Cliente' },
  { key: 'diferenciacion', label: 'Diferenciación' },
  { key: 'riesgos',        label: 'Riesgos' },
  { key: 'monetizacion',   label: 'Monetización' },
  { key: 'factibilidad',   label: 'Factibilidad' },
]

const chipValoracion: Record<string, string> = {
  'Fuerte':   'bg-[#DCEFE0] text-[#1F6B3E]',
  'Moderado': 'bg-[#F5E4B8] text-[#8A5F0E]',
  'Débil':    'bg-[#F5D6D3] text-[#8B2E24]',
}

const colorSemaforo: Record<string, string> = {
  verde:    '#2E7D4F',
  amarillo: '#B07A17',
  rojo:     '#B23A3A',
}

const borderChipSemaforo: Record<string, string> = {
  verde:    'border-[#2E7D4F]',
  amarillo: 'border-[#B07A17]',
  rojo:     'border-[#B23A3A]',
}

interface Idea { id: string; nombre: string }
interface ResultadoComparacion {
  idea_id: string
  nombre: string
  semaforo: 'verde' | 'amarillo' | 'rojo'
  criterios_evaluados: Record<string, string>
}

export default function Comparacion() {
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [seleccionadas, setSeleccionadas] = useState<string[]>([])
  const [resultados, setResultados] = useState<ResultadoComparacion[]>([])
  const [mostrarSelector, setMostrarSelector] = useState(false)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  // Cargar todas las ideas al montar
  useEffect(() => {
    getIdeas().then(setIdeas).catch(() => setError('Error al cargar ideas'))
  }, [])

  // Disparar comparación cada vez que cambia la selección
  useEffect(() => {
    if (seleccionadas.length < 1) { setResultados([]); return }
    setCargando(true)
    setError('')
    compararIdeas(seleccionadas)
      .then((data) => setResultados(data.ideas || []))
      .catch((e) => setError(e.message || 'Error al comparar'))
      .finally(() => setCargando(false))
  }, [seleccionadas])

  const quitarIdea = (id: string) =>
    setSeleccionadas((prev) => prev.filter((s) => s !== id))

  const agregarIdea = (id: string) => {
    if (!seleccionadas.includes(id)) setSeleccionadas((prev) => [...prev, id])
    setMostrarSelector(false)
  }

  return (
    <div className="min-h-screen bg-[#EDEFF2] flex">

      <Sidebar />

      {/* Contenido principal */}
      <main className="ml-52 flex-1 px-10 py-8">
        <h1 className="text-2xl font-bold text-[#10161F] tracking-tight mb-6"
          style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
          Comparación de ideas
        </h1>

        {/* Selector */}
        <div className="flex items-center gap-2 flex-wrap mb-6 relative">
          {seleccionadas.map((id) => {
            const idea = ideas.find((i) => i.id === id)
            const resultado = resultados.find((r) => r.idea_id === id)
            if (!idea) return null
            return (
              <span
                key={id}
                className={`flex items-center gap-2 bg-white border-2 ${resultado ? borderChipSemaforo[resultado.semaforo] : 'border-[#D2D6DC]'} rounded-sm px-3 py-1 text-sm text-[#10161F] font-medium`}
              >
                {idea.nombre}
                <button onClick={() => quitarIdea(id)} className="text-[#7A828E] hover:text-[#B23A3A] transition-colors text-xs ml-1">✕</button>
              </span>
            )
          })}

          <div className="relative">
            <button
              onClick={() => setMostrarSelector((v) => !v)}
              className="bg-[#2454C7] text-white text-sm font-medium px-4 py-1.5 rounded-sm hover:bg-[#1a3fa0] transition-colors"
            >
              + Agregar idea
            </button>
            {mostrarSelector && (
              <div className="absolute top-9 left-0 bg-white border border-[#D2D6DC] rounded-sm shadow-md z-10 min-w-[180px]">
                {ideas.filter((i) => !seleccionadas.includes(i.id)).length === 0 && (
                  <p className="px-4 py-2 text-sm text-[#5B6472]">No hay más ideas</p>
                )}
                {ideas
                  .filter((i) => !seleccionadas.includes(i.id))
                  .map((i) => (
                    <button
                      key={i.id}
                      onClick={() => agregarIdea(i.id)}
                      className="w-full text-left px-4 py-2 text-sm text-[#10161F] hover:bg-[#EDEFF2] transition-colors"
                    >
                      {i.nombre}
                    </button>
                  ))}
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-[#F5D6D3] border border-[#B23A3A] text-[#8B2E24] text-sm px-4 py-3 rounded-sm mb-4">
            {error}
          </div>
        )}

        {cargando && (
          <p className="text-sm text-[#5B6472] text-center mt-10">Cargando comparación...</p>
        )}

        {!cargando && seleccionadas.length === 0 && (
          <p className="text-sm text-[#5B6472] text-center mt-10">
            Seleccioná al menos una idea evaluada para comparar.
          </p>
        )}

        {!cargando && resultados.length > 0 && (
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${resultados.length}, minmax(280px, 1fr))` }}>
            {resultados.map((r) => (
              <div
                key={r.idea_id}
                className="bg-white border border-[#D2D6DC] border-t-[3px] rounded-sm px-5 py-5 shadow-sm"
                style={{ borderTopColor: colorSemaforo[r.semaforo] }}
              >
                <div className="flex justify-between items-center mb-5">
                  <span className="font-bold text-[#10161F] text-lg" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                    {r.nombre}
                  </span>
                  <ChipSemaforo semaforo={r.semaforo} />
                </div>
                <div className="flex flex-col">
                  {CRITERIOS.map(({ key, label }, index) => {
                    const valor = r.criterios_evaluados[key] || '—'
                    return (
                      <div
                        key={key}
                        className={`flex justify-between items-center py-2.5 ${index < CRITERIOS.length - 1 ? 'border-b border-[#EDEFF2]' : ''}`}
                      >
                        <span className="text-sm text-[#2454C7]">{label}</span>
                        <span className={`text-[10px] font-medium px-2.5 py-0.5 rounded-sm ${chipValoracion[valor] || 'bg-[#E2E4E8] text-[#5B6472]'}`}>
                          {valor}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}