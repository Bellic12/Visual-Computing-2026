import { useState } from 'react'
import { Parqueadero3D } from './Parqueadero3D'

const ENTRADAS = [
  { id: 'oeste', label: 'Entrada Izquierda', flecha: '←', descripcion: 'Lateral oeste' },
  { id: 'este',  label: 'Entrada Derecha',  flecha: '→', descripcion: 'Lateral este'  },
]

function instruccionesDesdeRuta(ruta, destino, entrada) {
  if (!ruta || ruta.length < 2 || !destino) return []

  const nombreEntrada = ENTRADAS.find((e) => e.id === entrada)?.label ?? entrada
  const instrucciones = [`Ingresa al parqueadero por la ${nombreEntrada}`]

  const dx = ruta.length >= 2 ? ruta[1].x - ruta[0].x : 0
  instrucciones.push(
    dx > 0
      ? 'Avanza hacia la derecha por el corredor central'
      : 'Avanza hacia la izquierda por el corredor central',
  )

  const fila = destino.id?.split('-')[1] ?? ''
  const haciaElNorte = (ruta[ruta.length - 1]?.z ?? 0) < 0
  instrucciones.push(`Gira hacia el ${haciaElNorte ? 'norte' : 'sur'} (Fila ${fila})`)
  instrucciones.push(`Estaciona en el espacio ${destino.id}`)

  return instrucciones
}

export function VistaUsuario({ espacios, reserva, cargando, errorReserva, solicitar, liberar }) {
  const [entrada, setEntrada] = useState('oeste')

  const pasos = instruccionesDesdeRuta(reserva?.ruta, reserva?.destino, reserva?.entrada ?? entrada)

  return (
    <div className="vista-usuario">
      {!reserva ? (
        <div className="vu-splash">
          <div className="vu-card">
            <p className="eyebrow" style={{ textAlign: 'center', marginBottom: '0.4rem' }}>
              Sistema de guía de parqueadero
            </p>
            <h2 className="vu-titulo">Bienvenido</h2>
            <p className="vu-hint">Selecciona la entrada por donde llegaste:</p>

            <div className="vu-entradas">
              {ENTRADAS.map((e) => (
                <button
                  key={e.id}
                  className={`vu-entrada-btn${entrada === e.id ? ' vu-entrada-btn--activa' : ''}`}
                  onClick={() => setEntrada(e.id)}
                >
                  <span className="vu-flecha">{e.flecha}</span>
                  <div>
                    <div className="vu-entrada-label">{e.label}</div>
                    <div className="vu-entrada-desc">{e.descripcion}</div>
                  </div>
                </button>
              ))}
            </div>

            {errorReserva && <p className="vu-error">{errorReserva}</p>}

            <button
              className="vu-solicitar-btn"
              onClick={() => solicitar(entrada)}
              disabled={cargando}
            >
              {cargando ? 'Buscando espacio…' : 'Obtener espacio disponible'}
            </button>
          </div>
        </div>
      ) : (
        <div className="vu-activo">
          <header className="vu-header-activo">
            <div>
              <p className="eyebrow">Espacio asignado</p>
              <h2 className="vu-titulo-activo">{reserva.espacio_id}</h2>
              <p className="vu-dist">
                Distancia desde tu entrada: <strong>{reserva.distancia} m</strong>
              </p>
            </div>
            <button className="vu-llegue-btn" onClick={liberar}>
              ✓ Ya llegué — liberar
            </button>
          </header>

          <div className="vu-contenido">
            <Parqueadero3D
              espacios={espacios}
              ruta={reserva.ruta}
              destino={reserva.destino}
              animarRuta
            />

            <nav className="vu-instrucciones" aria-label="Pasos de navegación">
              <h3 className="vu-instrucciones-titulo">Tu ruta</h3>
              <ol className="vu-pasos">
                {pasos.map((paso, i) => (
                  <li key={i} className="vu-paso">
                    <span className="vu-paso-num">{i + 1}</span>
                    <span>{paso}</span>
                  </li>
                ))}
              </ol>

              <div className="vu-leyenda-mini">
                <span><span className="vu-dot vu-dot--naranja" /> Guía</span>
                <span><span className="vu-dot vu-dot--azul" /> Destino</span>
              </div>
            </nav>
          </div>
        </div>
      )}
    </div>
  )
}
