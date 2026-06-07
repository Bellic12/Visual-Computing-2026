import { Dashboard } from './components/Dashboard'
import { Parqueadero3D } from './components/Parqueadero3D'
import { useEspacios } from './hooks/useEspacios'
import { useHistorialOcupacion } from './hooks/useHistorialOcupacion'
import './App.css'

function App() {
  const { espacios, stats, loading, error, updatedAt } = useEspacios()
  const historial = useHistorialOcupacion(stats)

  return (
    <main className="app-shell">
      <Dashboard
        stats={stats}
        loading={loading}
        error={error}
        updatedAt={updatedAt}
        historial={historial}
      />
      <Parqueadero3D espacios={espacios} />
    </main>
  )
}

export default App
