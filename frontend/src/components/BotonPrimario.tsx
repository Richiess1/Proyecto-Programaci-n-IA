interface Props {
  label: string
  onClick?: () => void
}

export default function BotonPrimario({ label, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="bg-[#2454C7] text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#1a3fa0] transition-colors"
    >
      {label}
    </button>
  )
}