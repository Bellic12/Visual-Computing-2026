import './App.css'
import { useThreeIkScene } from './useThreeIkScene'

function StatCard({ label, value, detail }) {
  return (
    <article className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      {detail ? <span className="stat-detail">{detail}</span> : null}
    </article>
  )
}

function App() {
  const {
    mountRef,
    metrics,
    iterations,
    setIterations,
    influence,
    setInfluence,
    autoTarget,
    setAutoTarget,
    resetPose,
    randomizeTarget,
  } = useThreeIkScene()

  return (
    <main className="experience-shell">
      <section className="intro-panel">
        <p className="eyebrow">Three.js / Cinemática inversa</p>
        <h1>Crea un brazo articulado que persigue objetivos en tiempo real</h1>
        <p className="summary">
          Esta escena resuelve una cadena de eslabones con CCD, permite arrastrar
          el objetivo sobre el plano y muestra si el brazo alcanza o no la meta.
        </p>

        <div className="status-row">
          <span className={`status-pill ${metrics.solved ? 'is-accent' : ''}`}>
            {metrics.solved ? 'Objetivo resuelto' : 'Ajustando postura'}
          </span>
          <span className={`status-pill ${metrics.reachable ? 'is-good' : 'is-warn'}`}>
            {metrics.reachable ? 'Dentro del alcance' : 'Fuera de alcance'}
          </span>
          <span className="status-pill is-muted">CCD activo</span>
        </div>

        <section className="control-panel" aria-label="Controles de la simulación">
          <div className="control-group">
            <div className="control-header">
              <span>Iteraciones por frame</span>
              <strong>{iterations}</strong>
            </div>
            <input
              aria-label="Iteraciones por frame"
              className="range"
              max="16"
              min="1"
              step="1"
              type="range"
              value={iterations}
              onChange={(event) => setIterations(Number(event.target.value))}
            />
          </div>

          <div className="control-group">
            <div className="control-header">
              <span>Intensidad del giro</span>
              <strong>{Math.round(influence * 100)}%</strong>
            </div>
            <input
              aria-label="Intensidad del giro"
              className="range"
              max="1"
              min="0.1"
              step="0.01"
              type="range"
              value={influence}
              onChange={(event) => setInfluence(Number(event.target.value))}
            />
          </div>

          <div className="button-row">
            <button type="button" className="primary-button" onClick={resetPose}>
              Reset pose
            </button>
            <button type="button" className="secondary-button" onClick={randomizeTarget}>
              Objetivo aleatorio
            </button>
            <button
              type="button"
              className={`secondary-button ${autoTarget ? 'is-active' : ''}`}
              onClick={() => setAutoTarget((value) => !value)}
            >
              {autoTarget ? 'Auto target on' : 'Auto target off'}
            </button>
          </div>
        </section>

        <section className="stats-grid" aria-label="Métricas de la simulación">
          <StatCard
            label="Error restante"
            value={`${metrics.distance.toFixed(2)} u`}
            detail="Distancia final entre la mano y el objetivo"
          />
          <StatCard
            label="Alcance total"
            value={`${metrics.chainLength.toFixed(2)} u`}
            detail="Suma de todos los segmentos del brazo"
          />
          <StatCard
            label="Distancia al objetivo"
            value={`${metrics.targetDistance.toFixed(2)} u`}
            detail="Separación entre la base y la esfera"
          />
          <StatCard
            label="Modo"
            value={metrics.mode}
            detail="Arrastra la esfera con el puntero sobre el plano"
          />
        </section>
      </section>

      <section className="viewer-panel">
        <div className="viewer-frame">
          <div ref={mountRef} className="viewport" />

          <div className="viewer-overlay">
            <p>
              Mueve el objetivo con el mouse o deja activo el recorrido automático.
            </p>
            <p>
              El solver reorienta los eslabones desde la mano hacia la base en cada
              frame.
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App