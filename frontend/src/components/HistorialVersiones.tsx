interface EvaluacionMock {
  version: number
  fecha: string
  color: 'verde' | 'amarillo' | 'rojo'
}

interface Props {
  historial: EvaluacionMock[]
}

export default function HistorialVersiones({ historial }: Props) {
  return (
    <div className="bg-white p-4 border border-[#D2D6DC] mb-4">
      <h3 className="text-[10px] font-bold text-[#5B6472] uppercase tracking-widest mb-4">Historial de versiones</h3>
      
      <div className="space-y-3">
        {historial.map((ev, index) => (
          <div key={index} className="flex items-center justify-between pb-3 border-b border-[#E2E4E8] last:border-0 last:pb-0">
            <div className="flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${ev.color === 'verde' ? 'bg-[#1E8E3E]' : ev.color === 'rojo' ? 'bg-[#D93025]' : 'bg-[#F9AB00]'}`}></span>
              <span className="text-[12px] font-bold text-[#10161F]">v{ev.version}</span>
            </div>
            <span className="text-[12px] text-[#5B6472]">{ev.fecha}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
