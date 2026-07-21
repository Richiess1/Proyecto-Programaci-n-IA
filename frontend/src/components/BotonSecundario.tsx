interface Props {
  label: string
  onClick?: () => void
}

export default function BotonSecundario({ label, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="border border-[#2454C7] text-[#2454C7] text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#EEF2FB] transition-colors"
    >
      {label}
    </button>
  )
}