import { useNavigate, useLocation } from 'react-router-dom'
import AvisoIA from './AvisoIA'
import logoEvaluador from '../assets/Evaluador.png'

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside className="w-52 bg-white border-r border-[#D2D6DC] flex flex-col px-4 py-6 gap-6 fixed h-full z-10 left-0 top-0">
      <div className="flex justify-center items-center py-2">
        <img src={logoEvaluador} alt="Evaluador de ideas de negocio" className="w-full h-auto object-contain max-w-[150px]" />
      </div>

      <button
        onClick={() => navigate('/registro')}
        className="bg-[#2454C7] text-white text-sm font-medium px-4 py-2 rounded-sm hover:bg-[#1a3fa0] transition-colors text-left"
      >
        + Nueva idea
      </button>

      <nav className="flex flex-col gap-1">
        <button
          onClick={() => navigate('/')}
          className={`text-sm text-left pl-2 transition-colors ${location.pathname === '/'
              ? 'text-[#10161F] font-medium border-l-[3px] border-[#2454C7]'
              : 'text-[#5B6472] hover:text-[#2454C7] border-l-[3px] border-transparent'
            }`}
        >
          Ideas
        </button>
        <button
          onClick={() => navigate('/comparar')}
          className={`text-sm text-left pl-2 transition-colors ${location.pathname === '/comparar'
              ? 'text-[#10161F] font-medium border-l-[3px] border-[#2454C7]'
              : 'text-[#5B6472] hover:text-[#2454C7] border-l-[3px] border-transparent'
            }`}
        >
          Comparar ideas
        </button>
      </nav>

      <div className="mt-auto">
        <AvisoIA />
      </div>
    </aside>
  )
}
