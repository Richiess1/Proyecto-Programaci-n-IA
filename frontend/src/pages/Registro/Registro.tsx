import FormularioIdea from '../../components/FormularioIdea'
import Sidebar from '../../components/Sidebar'

export default function Registro() {
  return (
    <div className="h-screen overflow-hidden bg-[#EDEFF2] flex">
      <Sidebar />
      <main className="ml-52 flex-1 h-screen overflow-hidden">
        <FormularioIdea />

      </main>
    </div>
  )
}