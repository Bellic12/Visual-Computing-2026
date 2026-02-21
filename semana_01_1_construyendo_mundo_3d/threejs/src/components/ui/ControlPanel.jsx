import ModelReferencePreview from './ModelReferencePreview'

const VIEW_MODE_LABELS = {
  vertices: 'Vértices',
  edges: 'Aristas',
  faces: 'Caras',
}

const SUPPORTED_EXTENSIONS_HINT = '.obj,.stl,.gltf,.glb'

function formatNumber(value) {
  return Intl.NumberFormat('es-ES').format(value)
}

function ControlPanel({
  selectedFileName,
  loadedModel,
  modelStats,
  viewMode,
  modelRotation,
  isLoading,
  loadingError,
  onModeChange,
  onRotateModel,
  onResetRotation,
  onFileSelected,
}) {
  const handleInputChange = (event) => {
    const selectedFile = event.target.files?.[0] ?? null
    onFileSelected(selectedFile)
  }

  return (
    <aside className="control-panel">
      <h1 className="panel-title">Visualizador de Modelos 3D</h1>

      <section>
        <h2 className="section-title">Archivo</h2>
        <input
          className="file-input"
          type="file"
          accept={SUPPORTED_EXTENSIONS_HINT}
          onChange={handleInputChange}
        />
        <p className="status">Seleccionado: {selectedFileName}</p>
      </section>

      <section>
        <h2 className="section-title">Modo de visualización</h2>
        <div className="mode-group" role="group" aria-label="Modo de visualización">
          {Object.entries(VIEW_MODE_LABELS).map(([mode, label]) => (
            <button
              key={mode}
              type="button"
              className={`mode-button ${viewMode === mode ? 'active' : ''}`}
              onClick={() => onModeChange(mode)}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      <section>
        <h2 className="section-title">Referencia</h2>
        <ModelReferencePreview loadedModel={loadedModel} modelRotation={modelRotation} />
      </section>

      <section>
        <h2 className="section-title">Orientación del modelo</h2>
        <div className="rotation-grid">
          <button type="button" className="mode-button" onClick={() => onRotateModel(0, 1)}>X +90°</button>
          <button type="button" className="mode-button" onClick={() => onRotateModel(0, -1)}>X -90°</button>
          <button type="button" className="mode-button" onClick={() => onRotateModel(1, 1)}>Y +90°</button>
          <button type="button" className="mode-button" onClick={() => onRotateModel(1, -1)}>Y -90°</button>
          <button type="button" className="mode-button" onClick={() => onRotateModel(2, 1)}>Z +90°</button>
          <button type="button" className="mode-button" onClick={() => onRotateModel(2, -1)}>Z -90°</button>
        </div>
        <button type="button" className="reset-button" onClick={onResetRotation}>Restablecer orientación</button>
      </section>

      <section>
        <h2 className="section-title">Estadísticas del modelo</h2>
        <ul className="meta-list">
          <li>Vértices: {formatNumber(modelStats.vertices)}</li>
          <li>Caras: {formatNumber(modelStats.faces)}</li>
          <li>Mallas: {formatNumber(modelStats.meshes)}</li>
        </ul>
      </section>

      {isLoading && <p className="status loading">Cargando modelo...</p>}
      {loadingError && <p className="status error">Error: {loadingError}</p>}
    </aside>
  )
}

export default ControlPanel