import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ChipSemaforo from '../../components/ChipSemaforo'
import AvisoIA from '../../components/AvisoIA'
import ideasMock from '../../mocks/ideas.json'

const evaluacionesMock: Record<string, {
  semaforo: 'verde' | 'amarillo' | 'rojo'
  estado: string
  version: number
  fecha: string
}> = {
  '40697a15-3e79-460f-b0a8-a02ed7ee0e5c': { semaforo: 'verde',    estado: 'aceptado',  version: 2, fecha: '10 JUL 2026' },
  'b1234567-89ab-cdef-0123-456789abcdef': { semaforo: 'amarillo', estado: 'pendiente', version: 1, fecha: '20 JUL 2026' },
  'c9876543-21fe-dcba-9876-543210fedcba': { semaforo: 'rojo',     estado: 'pendiente', version: 1, fecha: '1 JUL 2026'  },
}

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
  aceptado:  'bg-[#DCEFE0] text-[#1F6B3E]',
  pendiente: 'bg-[#E2E4E8] text-[#5B6472]',
  descartado:'bg-[#F5D6D3] text-[#8B2E24]',
}

export default function Listado() {
  const navigate = useNavigate()
  const [busqueda, setBusqueda] = useState('')

  const ideasFiltradas = ideasMock.filter((idea) =>
    idea.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    idea.sector.toLowerCase().includes(busqueda.toLowerCase()) ||
    idea.descripcion.toLowerCase().includes(busqueda.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-[#EDEFF2] flex">

      {/* Sidebar */}
      <aside className="w-52 bg-white border-r border-[#D2D6DC] flex flex-col px-4 py-6 gap-6 fixed h-full">
        <div>
          <p className="font-bold text-[#10161F] text-base tracking-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            EVALUADOR
          </p>
          <p className="text-[11px] text-[#2454C7]">de ideas de negocio</p>
        </div>

        <button
          onClick={() => navigate('/registro')}
          className="bg-[#2454C7] text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#1a3fa0] transition-colors text-left"
        >
          + Nueva idea
        </button>

        <nav className="flex flex-col gap-1">
          <span className="text-[#10161F] text-sm font-medium border-l-[3px] border-[#2454C7] pl-2">
            Ideas
          </span>
          <button
            onClick={() => navigate('/comparar')}
            className="text-[#5B6472] text-sm text-left pl-2 hover:text-[#2454C7] transition-colors"
          >
            Comparar ideas
          </button>
        </nav>

        <div className="mt-auto">
          <AvisoIA />
        </div>
      </aside>

      {/* Contenido principal */}
      <main className="ml-52 flex-1 px-10 py-8">

        {/* Header */}
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

        {/* Buscador */}
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

        {/* Lista de ideas */}
        <div className="flex flex-col gap-3">
          {ideasFiltradas.length === 0 && (
            <p className="text-sm text-[#5B6472] text-center mt-10">No se encontraron ideas.</p>
          )}
          {ideasFiltradas.map((idea) => {
            const eval_ = evaluacionesMock[idea.id]
            const inicial = idea.nombre.charAt(0).toUpperCase()
            const avatarColor = eval_ ? colorAvatar[eval_.semaforo] : 'bg-[#2454C7]'
            const bordeColor  = eval_ ? colorBorde[eval_.semaforo]  : '#2454C7'

            return (
              <div
                key={idea.id}
                onClick={() => navigate(`/ideas/${idea.id}`)}
                className="bg-white border border-[#D2D6DC] border-l-[4px] rounded-sm px-5 py-4 cursor-pointer hover:shadow-sm transition-shadow"
                style={{ borderLeftColor: bordeColor }}
              >
                <div className="flex items-start gap-4">

                  {/* Avatar con inicial */}
                  <div className={`${avatarColor} text-white font-bold text-sm w-9 h-9 rounded-sm flex items-center justify-center flex-shrink-0`}>
                    {inicial}
                  </div>

                  {/* Contenido */}
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-[#10161F] text-[15px]" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                          {idea.nombre}
                        </span>
                        {eval_ && <ChipSemaforo semaforo={eval_.semaforo} />}
                        {eval_ && (
                          <span className={`text-[9px] font-medium tracking-widest px-2 py-0.5 rounded-sm uppercase ${chipEstado[eval_.estado]}`}>
                            {eval_.estado}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                        <span className="text-[11px] text-[#7A828E]">
                          {eval_ ? `V${eval_.version} · ${eval_.fecha}` : 'SIN EVALUAR'}
                        </span>
                        <span className="text-[#D2D6DC] hover:text-[#B07A17] cursor-pointer transition-colors">☆</span>
                        <span className="text-[#2454C7] text-sm">→</span>
                      </div>
                    </div>

                    <p className="text-[10px] text-[#5B6472] tracking-wide mt-1 uppercase">
                      {idea.sector}
                    </p>

                    <p className="text-[12px] text-[#232B36] mt-2 leading-relaxed line-clamp-2">
                      {idea.descripcion}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}