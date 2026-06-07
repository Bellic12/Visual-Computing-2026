import { useEffect, useState } from 'react'
import { Parqueadero3D } from './Parqueadero3D'
import { useEspacios } from '../hooks/useEspacios'
import { useReserva } from '../hooks/useReserva'

const CONFIG = {
  oeste: { label: 'Entrada Izquierda', flecha: '←', lado: 'Lateral oeste' },
  este:  { label: 'Entrada Derecha',   flecha: '→', lado: 'Lateral este'  },
}

function instrucciones(ruta, destino, entrada) {
  if (!ruta || ruta.length < 2 || !destino) return []
  const cfg = CONFIG[entrada]
  const dx = ruta[1].x - ruta[0].x
  const fila = destino.id?.split('-')[1] ?? ''
  const haciaElNorte = (ruta[ruta.length - 1]?.z ?? 0) < 0
  return [
    `Ingresa por la ${cfg.label}`,
    dx > 0 ? 'Avanza hacia la derecha por el corredor central' : 'Avanza hacia la izquierda por el corredor central',
    `Gira hacia el ${haciaElNorte ? 'norte' : 'sur'} (Fila ${fila})`,
    `Estaciona en el espacio ${destino.id}`,
  ]
}

export function EntradaScreen({ entrada }) {
  const { espacios, stats } = useEspacios()
  const { reserva, cargando, error, solicitar, liberar } = useReserva()
  const cfg = CONFIG[entrada]

  const RESET_SEG = 20
  const [cuenta, setCuenta] = useState(RESET_SEG)

  // Countdown + auto-reset 20 s after assignment
  useEffect(() => {
    if (!reserva) { setCuenta(RESET_SEG); return }
    setCuenta(RESET_SEG)
    const intervalo = setInterval(() => {
      setCuenta((c) => {
        if (c <= 1) { clearInterval(intervalo); liberar(); return 0 }
        return c - 1
      })
    }, 1000)
    return () => clearInterval(intervalo)
  }, [reserva, liberar])

  const pasos = instrucciones(reserva?.ruta, reserva?.destino, entrada)

  /* ── Idle state ─────────────────────────────────────────────────────── */
  if (!reserva) {
    return (
      <div className="entrada-idle">
        <div className="entrada-idle__top">
          <span className="entrada-idle__flecha">{cfg.flecha}</span>
          <div>
            <h1 className="entrada-idle__title">{cfg.label}</h1>
            <p className="entrada-idle__lado">{cfg.lado}</p>
          </div>
        </div>

        <div className="entrada-idle__stats">
          <div className="entrada-stat">
            <span className="entrada-stat__num">{stats.libres}</span>
            <span className="entrada-stat__lbl">Espacios libres</span>
          </div>
          <div className="entrada-stat entrada-stat--sep" />
          <div className="entrada-stat">
            <span className="entrada-stat__num">{stats.total}</span>
            <span className="entrada-stat__lbl">Total</span>
          </div>
          <div className="entrada-stat entrada-stat--sep" />
          <div className="entrada-stat">
            <span className="entrada-stat__num">{stats.ocupacion}%</span>
            <span className="entrada-stat__lbl">Ocupación</span>
          </div>
        </div>

        {error && <p className="entrada-error">{error}</p>}

        <button
          className="entrada-btn-solicitar"
          onClick={() => solicitar(entrada)}
          disabled={cargando}
        >
          {cargando ? 'Buscando espacio…' : 'Solicitar espacio'}
        </button>
      </div>
    )
  }

  /* ── Active state — route shown ─────────────────────────────────────── */
  return (
    <div className="entrada-activa">
      <header className="entrada-activa__header">
        <div className="entrada-activa__info">
          <p className="eyebrow">{cfg.label} — Espacio asignado</p>
          <h1 className="entrada-activa__espacio">{reserva.espacio_id}</h1>
          <p className="entrada-activa__dist">
            Distancia: <strong>{reserva.distancia} m</strong>
          </p>
        </div>
        <div className="entrada-activa__acciones">
          <button className="entrada-btn-entendido" onClick={liberar}>
            Entendido
          </button>
          <p className="entrada-activa__reset">
            Se reinicia en <strong>{cuenta}s</strong>
          </p>
        </div>
      </header>

      <div className="entrada-activa__mapa">
        <Parqueadero3D
          espacios={espacios}
          ruta={reserva.ruta}
          destino={reserva.destino}
          animarRuta
        />
      </div>

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
  )
}
