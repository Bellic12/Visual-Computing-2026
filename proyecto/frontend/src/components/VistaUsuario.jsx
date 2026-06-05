import { useState } from 'react'
import { Parqueadero3D } from './Parqueadero3D'

const ENTRADAS = [
  { id: 'noroeste', label: 'Noroeste', flecha: '↖' },
  { id: 'noreste', label: 'Noreste', flecha: '↗' },
  { id: 'suroeste', label: 'Suroeste', flecha: '↙' },
  { id: 'sureste', label: 'Sureste', flecha: '↘' },
]

function instruccionesDesdeRuta(ruta, destino, entrada) {
  if (!ruta || ruta.length < 2) return []

  const nombreEntrada = ENTRADAS.find((e) => e.id === entrada)?.label ?? entrada

  const instrucciones = [`Ingresa al parqueadero por la entrada ${nombreEntrada}`]

  for (let i = 1; i < ruta.length; i++) {
    const dx = ruta[i].x - ruta[i - 1].x
    const dz = ruta[i].z - ruta[i - 1].z
    const esUltimo = i === ruta.length - 1

    if (esUltimo) {
      instrucciones.push(`Estaciona en el espacio ${destino?.id ?? ''}`)
    } else if (Math.abs(dx) > Math.abs(dz)) {
      instrucciones.push(dx > 0 ? 'Avanza hacia la derecha al corredor lateral' : 'Avanza hacia la izquierda al corredor lateral')
    } else {
      instrucciones.push(`Avanza por el corredor hasta la fila ${destino?.id?.split('-')[1] ?? ''}`)
    }
  }

  return instrucciones
}

export function VistaUsuario({ espacios, reserva, cargando, errorReserva, solicitar, liberar }) {
  const [entrada, setEntrada] = useState('noroeste')

  const pasos = instruccionesDesdeRuta(reserva?.ruta, reserva?.destino, reserva?.entrada ?? entrada)

  return (
    <div className="vista-usuario">
      <header className="vu-header">
        <div>
          <p className="eyebrow">Sistema de guia</p>
          <h2 className="vu-titulo">
            {reserva ? `Espacio asignado: ${reserva.espacio_id}` : 'Bienvenido al Parqueadero'}
          </h2>
          {reserva ? (
            <p className="vu-subtitulo">
              Distancia desde la entrada: <strong>{reserva.distancia} m</strong>
            </p>
          ) : (
            <p className="vu-subtitulo">
              Selecciona tu entrada y solicita un espacio disponible.
            </p>
          )}
        </div>
      </header>

      {!reserva ? (
        <div className="vu-seleccion">
          <p className="vu-label">Selecciona tu entrada:</p>
          <div className="vu-entradas">
            {ENTRADAS.map((e) => (
              <button
                key={e.id}
                className={`vu-entrada-btn${entrada === e.id ? ' vu-entrada-btn--activa' : ''}`}
                onClick={() => setEntrada(e.id)}
              >
                <span className="vu-flecha">{e.flecha}</span>
                <span>{e.label}</span>
              </button>
            ))}
          </div>
          {errorReserva && <p className="vu-error">{errorReserva}</p>}
          <button
            className="vu-solicitar-btn"
            onClick={() => solicitar(entrada)}
            disabled={cargando}
          >
            {cargando ? 'Buscando espacio...' : 'Solicitar espacio'}
          </button>
        </div>
      ) : (
        <div className="vu-activo">
          <div className="vu-contenido">
            <Parqueadero3D
              espacios={espacios}
              ruta={reserva.ruta}
              destino={reserva.destino}
              animarRuta
            />

            <aside className="vu-instrucciones">
              <h3>Instrucciones</h3>
              <ol className="vu-pasos">
                {pasos.map((paso, i) => (
                  <li key={i} className="vu-paso">
                    <span className="vu-paso-num">{i + 1}</span>
                    <span>{paso}</span>
                  </li>
                ))}
              </ol>
              <div className="vu-leyenda-mini">
                <span className="vu-dot vu-dot--naranja" /> Punto de guia animado
                <span className="vu-dot vu-dot--azul" style={{ marginLeft: '0.8rem' }} /> Tu espacio
              </div>
              <button className="vu-llegue-btn" onClick={liberar}>
                He llegado — Liberar espacio
              </button>
            </aside>
          </div>
        </div>
      )}
    </div>
  )
}
