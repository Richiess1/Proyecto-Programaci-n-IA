interface Props {
  estadoActual: 'PENDIENTE' | 'ACEPTADO' | 'DESCARTADO'
  onCambiarEstado: (nuevoEstado: 'PENDIENTE' | 'ACEPTADO' | 'DESCARTADO') => void
}

export default function ControlEstado({ estadoActual, onCambiarEstado }: Props) {
  const btnBase = "w-full text-left text-[11px] font-bold tracking-widest uppercase px-4 py-2 border transition-colors mb-2 last:mb-0"
  
  return (
    <div className="bg-white border border-[#D2D6DC] p-4 mb-4">
      <h3 className="text-[10px] font-bold text-[#5B6472] uppercase tracking-widest mb-3">Estado</h3>
      
      <button
        onClick={() => onCambiarEstado('PENDIENTE')}
        className={`${btnBase} ${estadoActual === 'PENDIENTE' ? 'bg-[#F8F9FA] border-[#D2D6DC] text-[#10161F]' : 'bg-transparent border-[#E2E4E8] text-[#5B6472]'}`}
      >
        Pendiente
      </button>
      
      <button
        onClick={() => onCambiarEstado('ACEPTADO')}
        className={`${btnBase} ${estadoActual === 'ACEPTADO' ? 'bg-[#EAF3EC] border-[#1F6B3E]/30 text-[#1F6B3E]' : 'bg-transparent border-[#E2E4E8] text-[#5B6472]'}`}
      >
        Aceptado
      </button>
      
      <button
        onClick={() => onCambiarEstado('DESCARTADO')}
        className={`${btnBase} ${estadoActual === 'DESCARTADO' ? 'bg-[#FCE8E6] border-[#D93025]/30 text-[#A50E0E]' : 'bg-transparent border-[#E2E4E8] text-[#5B6472]'}`}
      >
        Descartado
      </button>
    </div>
  )
}
