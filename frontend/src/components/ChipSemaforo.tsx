interface Props {
  semaforo: 'verde' | 'amarillo' | 'rojo'
}

const config = {
  verde:    { label: 'VERDE',    bg: 'bg-[#DCEFE0]', text: 'text-[#1F6B3E]' },
  amarillo: { label: 'AMARILLO', bg: 'bg-[#F5E4B8]', text: 'text-[#8A5F0E]' },
  rojo:     { label: 'ROJO',     bg: 'bg-[#F5D6D3]', text: 'text-[#8B2E24]' },
}

export default function ChipSemaforo({ semaforo }: Props) {
  const { label, bg, text } = config[semaforo]
  return (
    <span className={`${bg} ${text} text-[10px] font-medium tracking-widest px-2 py-0.5 rounded-sm`}>
      {label}
    </span>
  )
}