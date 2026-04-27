import { Dashboard } from './components/Dashboard'
import { Parqueadero3D } from './components/Parqueadero3D'
import { useEspacios } from './hooks/useEspacios'
import './App.css'

function App() {
  const { espacios, ruta, destino, stats, loading, error, updatedAt } = useEspacios(5000)

  return (
    <main className="app-shell">
      <Dashboard stats={stats} loading={loading} error={error} updatedAt={updatedAt} />
      <Parqueadero3D espacios={espacios} ruta={ruta} destino={destino} />
    </main>
  )
}

export default App
