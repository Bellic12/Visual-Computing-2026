import { useState, useEffect } from 'react'
import { Dashboard } from './components/Dashboard'
import { Parqueadero3D } from './components/Parqueadero3D'
import { EntradaScreen } from './components/EntradaScreen'
import { useEspacios } from './hooks/useEspacios'
import { useHistorialOcupacion } from './hooks/useHistorialOcupacion'
import './App.css'

function AdminPage() {
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

function getHash() {
  const h = window.location.hash
  if (h.includes('oeste')) return 'oeste'
  if (h.includes('este'))  return 'este'
  return 'admin'
}

function App() {
  const [pagina, setPagina] = useState(getHash)

  useEffect(() => {
    const handler = () => setPagina(getHash())
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  if (pagina === 'oeste') return <EntradaScreen key="oeste" entrada="oeste" />
  if (pagina === 'este')  return <EntradaScreen key="este" entrada="este" />

  return (
    <>
      <nav className="navbar">
        <span className="navbar-brand">Smart Parking</span>
        <div className="navbar-links">
          <a className="navbar-btn navbar-btn--active" href="#/admin">Admin</a>
          <a className="navbar-btn" href="#/oeste" target="_blank" rel="noopener">Entrada Izq.</a>
          <a className="navbar-btn" href="#/este"  target="_blank" rel="noopener">Entrada Der.</a>
        </div>
      </nav>
      <AdminPage />
    </>
  )
}

export default App
