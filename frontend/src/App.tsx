import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Listado from './pages/Listado/Listado'
import Registro from './pages/Registro/Registro'
import Detalle from './pages/Detalle/Detalle'
import Comparacion from './pages/Comparacion/Comparacion'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Listado />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/ideas/:id" element={<Detalle />} />
        <Route path="/comparar" element={<Comparacion />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App