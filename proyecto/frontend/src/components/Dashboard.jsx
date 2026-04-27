function MetricCard({ label, value, tone = 'neutral' }) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <p className="metric-card__label">{label}</p>
      <p className="metric-card__value">{value}</p>
    </article>
  )
}

export function Dashboard({ stats, loading, error, updatedAt }) {
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
          <p className="eyebrow">Laboratorio virtual</p>
          <h1>Simulador de Parqueadero</h1>
          <p>
            Escenario de prueba para validar deteccion y posicionamiento de espacios en
            3D.
          </p>
        </div>
        <div className="dashboard__status">
          <span className={`status-dot ${error ? 'status-dot--down' : 'status-dot--up'}`} />
          {error ? `API con error: ${error}` : `API activa - Ultima lectura ${hora}`}
        </div>
      </header>

      <div className="metric-grid">
        <MetricCard label="Espacios Totales" value={loading ? '...' : stats.total} />
        <MetricCard label="Ocupados" value={loading ? '...' : stats.ocupados} tone="busy" />
        <MetricCard label="Libres" value={loading ? '...' : stats.libres} tone="free" />
        <MetricCard
          label="Ocupacion"
          value={loading ? '...' : `${stats.ocupacion}%`}
          tone="accent"
        />
      </div>
    </section>
  )
}
