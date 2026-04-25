import { Routes, Route } from 'react-router-dom'
import Menu from './components/Menu'
import Juego from './components/Juego'
import Creditos from './components/Creditos'
import './App.css'

export default function App() {
  return (
    <div className="app-shell">
      <Routes>
        <Route path="/" element={<Menu />} />
        <Route path="/juego" element={<Juego />} />
        <Route path="/creditos" element={<Creditos />} />
        <Route path="*" element={<Menu />} />
      </Routes>
    </div>
  )
}
