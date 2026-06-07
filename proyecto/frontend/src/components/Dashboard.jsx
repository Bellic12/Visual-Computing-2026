import { useRef } from 'react'
import { OcupacionChart } from './OcupacionChart'

function MetricCard({ label, value, tone = 'neutral' }) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <p className="metric-card__label">{label}</p>
      <p className="metric-card__value">{value}</p>
    </article>
  )
}

export function Dashboard({ stats, loading, error, updatedAt, historial }) {
  const peakRef = useRef(0)
  const prevPctRef = useRef(null)

  if (!loading && stats.total > 0) {
    peakRef.current = Math.max(peakRef.current, stats.ocupacion)
  }

  let tendencia = '→'
  let tendenciaTone = 'neutral'
  if (prevPctRef.current !== null && stats.total > 0) {
    if (stats.ocupacion > prevPctRef.current) { tendencia = '↑ Subiendo'; tendenciaTone = 'busy' }
    else if (stats.ocupacion < prevPctRef.current) { tendencia = '↓ Bajando'; tendenciaTone = 'free' }
    else { tendencia = '→ Estable'; tendenciaTone = 'neutral' }
  }
  if (!loading && stats.total > 0) prevPctRef.current = stats.ocupacion

  const hora = updatedAt
    ? new Intl.DateTimeFormat('es-CO', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }).format(updatedAt)
    : '--:--:--'

  return (
    <section className="dashboard" aria-label="Resumen del parqueadero">
      <header className="dashboard__header">
        <div>
          <p className="eyebrow">Administración · Vista en tiempo real</p>
          <h1>Parqueadero UFPR 1a</h1>
          <p>Monitoreo de ocupación y disponibilidad de espacios.</p>
        </div>
        <div className="dashboard__status">
          <span className={`status-dot ${error ? 'status-dot--down' : 'status-dot--up'}`} />
          {error ? `API con error: ${error}` : `API activa · Última lectura ${hora}`}
        </div>
      </header>

      <div className="metric-grid">
        <MetricCard label="Espacios Totales"  value={loading ? '…' : stats.total} />
        <MetricCard label="Ocupados"          value={loading ? '…' : stats.ocupados}       tone="busy" />
        <MetricCard label="Libres"            value={loading ? '…' : stats.libres}         tone="free" />
        <MetricCard label="Ocupación"         value={loading ? '…' : `${stats.ocupacion}%`} tone="accent" />
        <MetricCard label="Pico (sesión)"     value={loading ? '…' : `${peakRef.current}%`} />
        <MetricCard label="Tendencia"         value={loading ? '…' : tendencia}            tone={tendenciaTone} />
      </div>

      <div className="chart-section">
        <p className="chart-label">Uso por hora · sesión actual</p>
        <OcupacionChart historial={historial} />
      </div>
    </section>
  )
}
