interface Props {
  semaforo: 'VERDE' | 'AMARILLO' | 'ROJO'
  resumen: string
}

export default function BannerSemaforo({ semaforo, resumen }: Props) {
  const getStyle = () => {
    if (semaforo === 'VERDE') return 'bg-[#EAF3EC] text-[#1F6B3E] border-t-[3px] border-[#1F6B3E]'
    if (semaforo === 'AMARILLO') return 'bg-[#FEF7E0] text-[#B06000] border-t-[3px] border-[#F9AB00]'
    return 'bg-[#FCE8E6] text-[#A50E0E] border-t-[3px] border-[#D93025]'
  }

  return (
    <div className={`p-4 mb-4 ${getStyle()}`}>
      <span className="inline-block bg-white text-[10px] font-bold tracking-widest uppercase px-2 py-1 mb-2">
        {semaforo}
      </span>
      <p className="text-[13px] text-[#10161F] leading-relaxed">
        {resumen}
      </p>
    </div>
  )
}
