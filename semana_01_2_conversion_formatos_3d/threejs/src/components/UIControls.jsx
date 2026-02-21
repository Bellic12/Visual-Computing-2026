import { FORMAT_OPTIONS } from '../utils/modelUtils'

export default function UIControls({ activeFormat, onFormatChange, modelInfo }) {
  return (
    <aside className="ui-panel">
      <h2>Controles</h2>

      <div className="format-buttons" role="group" aria-label="Cambiar formato">
        {FORMAT_OPTIONS.map((format) => (
          <button
            key={format}
            type="button"
            className={`format-button ${activeFormat === format ? 'active' : ''}`}
            onClick={() => onFormatChange(format)}
          >
            {format}
          </button>
        ))}
      </div>

      <div className="ui-block">
        <h2>Información del modelo</h2>
        <div className="info-grid">
          <div className="info-row">
            <span>Formato:</span>
            <strong>{modelInfo.format}</strong>
          </div>
          <div className="info-row">
            <span>Vértices:</span>
            <strong>{modelInfo.vertices.toLocaleString()}</strong>
          </div>
          <div className="info-row">
            <span>Caras:</span>
            <strong>{modelInfo.faces.toLocaleString()}</strong>
          </div>
        </div>
      </div>

      <p className="scene-hint">
        Usa OrbitControls: arrastra para rotar, rueda para zoom y botón derecho para desplazar.
      </p>
    </aside>
  )
}
