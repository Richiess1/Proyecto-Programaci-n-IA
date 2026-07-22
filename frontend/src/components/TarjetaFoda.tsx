interface FodaProps {
  foda: {
    fortalezas: string[]
    debilidades: string[]
    oportunidades: string[]
    amenazas: string[]
  }
}

export default function TarjetaFoda({ foda }: FodaProps) {
  const Section = ({ title, items, topBorderColor, titleColor }: { title: string, items: string[], topBorderColor: string, titleColor: string }) => (
    <div className={`bg-white border border-[#D2D6DC] ${topBorderColor} p-4 h-full`}>
      <h4 className={`text-[10px] font-bold uppercase tracking-widest mb-3 ${titleColor}`}>{title}</h4>
      <ul className="space-y-2">
        {items.map((item, idx) => (
          <li key={idx} className="text-[13px] text-[#10161F] flex items-start">
            <span className="mr-2 mt-0.5">•</span>
            <span className="leading-relaxed">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )

  return (
    <div className="mb-6">
      <h3 className="text-sm font-bold text-[#10161F] mb-3">FODA</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Section title="Fortalezas" items={foda.fortalezas} topBorderColor="border-t-[3px] border-t-[#1E8E3E]" titleColor="text-[#1E8E3E]" />
        <Section title="Debilidades" items={foda.debilidades} topBorderColor="border-t-[3px] border-t-[#D93025]" titleColor="text-[#D93025]" />
        <Section title="Oportunidades" items={foda.oportunidades} topBorderColor="border-t-[3px] border-t-[#2454C7]" titleColor="text-[#2454C7]" />
        <Section title="Amenazas" items={foda.amenazas} topBorderColor="border-t-[3px] border-t-[#F9AB00]" titleColor="text-[#B06000]" />
      </div>
    </div>
  )
}
