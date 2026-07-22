import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ChipSemaforo from '../../components/ChipSemaforo'
import Sidebar from '../../components/Sidebar'
import { getIdeas, getEvaluaciones } from '../../services/apiClient'

const colorBorde: Record<string, string> = {
  verde:    '#2E7D4F',
  amarillo: '#B07A17',
  rojo:     '#B23A3A',
}

const colorAvatar: Record<string, string> = {
  verde:    'bg-[#2E7D4F]',
  amarillo: 'bg-[#B07A17]',
  rojo:     'bg-[#B23A3A]',
}

const chipEstado: Record<string, string> = {
  aceptado:   'bg-[#DCEFE0] text-[#1F6B3E]',
  pendiente:  'bg-[#E2E4E8] text-[#5B6472]',
  descartado: 'bg-[#F5D6D3] text-[#8B2E24]',
}

interface Evaluacion {
  id: string
  idea_id: string
  version: number
  fecha: string
  estado: string
  resultado: { semaforo: 'verde' | 'amarillo' | 'rojo' }
}

interface Idea {
  id: string
  nombre: string
  descripcion: string
  sector: string
}

export default function Listado() {
  const navigate = useNavigate()
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [evaluaciones, setEvaluaciones] = useState<Record<string, Evaluacion>>({})
  const [busqueda, setBusqueda] = useState('')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function cargar() {
      try {
        const data = await getIdeas()
        setIdeas(data)
        // traer última evaluación de cada idea
        const evals: Record<string, Evaluacion> = {}
        await Promise.all(
          data.map(async (idea: Idea) => {
            try {
              const lista = await getEvaluaciones(idea.id)
              if (lista.length > 0) {
                // la más reciente es la última del array
                evals[idea.id] = lista[lista.length - 1]
              }
            } catch {
              // si no tiene evaluaciones, simplemente no se agrega
            }
          })
        )
        setEvaluaciones(evals)
      } catch (e: any) {
        setError(e.message || 'Error al cargar las ideas')
      } finally {
        setCargando(false)
      }
    }
    cargar()
  }, [])

  const ideasFiltradas = ideas.filter((idea) =>
    idea.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    idea.sector?.toLowerCase().includes(busqueda.toLowerCase()) ||
    idea.descripcion.toLowerCase().includes(busqueda.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-[#EDEFF2] flex">

      <Sidebar />

      {/* Contenido principal */}
      <main className="ml-52 flex-1 px-10 py-8">
        <div className="flex justify-between items-start mb-1">
          <div>
            <h1 className="text-2xl font-bold text-[#10161F] tracking-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
              Tus ideas de negocio
            </h1>
            <p className="text-sm text-[#5B6472] mt-1">{ideasFiltradas.length} ideas registradas</p>
          </div>
          <button
            onClick={() => navigate('/registro')}
            className="bg-[#2454C7] text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#1a3fa0] transition-colors"
          >
            + Nueva idea
          </button>
        </div>

        <div className="relative mb-5 mt-4">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#5B6472] text-sm">🔍</span>
          <input
            type="text"
            placeholder="Buscar por nombre, sector o descripción"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full bg-white border border-[#D2D6DC] rounded-sm pl-9 pr-4 py-2 text-sm text-[#10161F] placeholder-[#7A828E] focus:outline-none focus:border-[#2454C7]"
          />
        </div>

        {cargando && (
          <p className="text-sm text-[#5B6472] text-center mt-10">Cargando ideas...</p>
        )}

        {error && (
          <div className="bg-[#F5D6D3] border border-[#B23A3A] text-[#8B2E24] text-sm px-4 py-3 rounded-sm mt-4">
            {error}
          </div>
        )}

        {!cargando && !error && (
          <div className="flex flex-col gap-3">
            {ideasFiltradas.length === 0 && (
              <p className="text-sm text-[#5B6472] text-center mt-10">No se encontraron ideas.</p>
            )}
            {ideasFiltradas.map((idea) => {
              const eval_ = evaluaciones[idea.id]
              const inicial = idea.nombre.charAt(0).toUpperCase()
              const semaforo = eval_?.resultado?.semaforo
              const avatarColor = semaforo ? colorAvatar[semaforo] : 'bg-[#2454C7]'
              const bordeColor  = semaforo ? colorBorde[semaforo]  : '#2454C7'

              return (
                <div
                  key={idea.id}
                  onClick={() => navigate(`/ideas/${idea.id}`)}
                  className="bg-white border border-[#D2D6DC] border-l-[4px] rounded-sm px-5 py-4 cursor-pointer hover:shadow-sm transition-shadow"
                  style={{ borderLeftColor: bordeColor }}
                >
                  <div className="flex items-start gap-4">
                    <div className={`${avatarColor} text-white font-bold text-sm w-9 h-9 rounded-sm flex items-center justify-center flex-shrink-0`}>
                      {inicial}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-bold text-[#10161F] text-[15px]" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                            {idea.nombre}
                          </span>
                          {semaforo && <ChipSemaforo semaforo={semaforo} />}
                          {eval_?.estado && (
                            <span className={`text-[9px] font-medium tracking-widest px-2 py-0.5 rounded-sm uppercase ${chipEstado[eval_.estado] || 'bg-[#E2E4E8] text-[#5B6472]'}`}>
                              {eval_.estado}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                          <span className="text-[11px] text-[#7A828E]">
                            {eval_
                              ? `V${eval_.version} · ${new Date(eval_.fecha).toLocaleDateString('es-SV', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}`
                              : 'SIN EVALUAR'}
                          </span>
                          <span className="text-[#D2D6DC] hover:text-[#B07A17] cursor-pointer transition-colors">☆</span>
                          <span className="text-[#2454C7] text-sm">→</span>
                        </div>
                      </div>
                      <p className="text-[10px] text-[#5B6472] tracking-wide mt-1 uppercase">{idea.sector}</p>
                      <p className="text-[12px] text-[#232B36] mt-2 leading-relaxed line-clamp-2">{idea.descripcion}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}