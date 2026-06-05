import { useState } from 'react'
import { Dashboard } from './components/Dashboard'
import { Parqueadero3D } from './components/Parqueadero3D'
import { VistaUsuario } from './components/VistaUsuario'
import { useEspacios } from './hooks/useEspacios'
import { useReserva } from './hooks/useReserva'
import './App.css'

function App() {
  const [vista, setVista] = useState('admin')
  const { espacios, ruta, destino, stats, loading, error, updatedAt } = useEspacios()
  const { reserva, cargando, error: errorReserva, solicitar, liberar } = useReserva()

  return (
    <main className="app-shell">
      <nav className="tab-nav">
        <button
          className={`tab-btn${vista === 'admin' ? ' tab-btn--activo' : ''}`}
          onClick={() => setVista('admin')}
        >
          Vista Administrador
        </button>
        <button
          className={`tab-btn${vista === 'usuario' ? ' tab-btn--activo' : ''}`}
          onClick={() => setVista('usuario')}
        >
          Vista Usuario
          {reserva ? <span className="tab-badge" /> : null}
        </button>
      </nav>

      {vista === 'admin' ? (
        <>
          <Dashboard stats={stats} loading={loading} error={error} updatedAt={updatedAt} />
          <Parqueadero3D espacios={espacios} ruta={ruta} destino={destino} />
        </>
      ) : (
        <VistaUsuario
          espacios={espacios}
          reserva={reserva}
          cargando={cargando}
          errorReserva={errorReserva}
          solicitar={solicitar}
          liberar={liberar}
        />
      )}
    </main>
  )
}

export default App
