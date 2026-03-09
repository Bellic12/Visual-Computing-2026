function ControlRow({ label, min, max, step, value, onChange }) {
  const handleNumericChange = (rawValue) => {
    const nextValue = Number(rawValue)
    if (Number.isFinite(nextValue)) {
      onChange(nextValue)
    }
  }

  return (
    <label className="control-row">
      <span>{label}</span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => handleNumericChange(event.target.value)}
      />
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => handleNumericChange(event.target.value)}
      />
    </label>
  )
}

export function ControlPanel({
  cameraState,
  setCameraValue,
  distortionState,
  setDistortionValue,
  projectionData,
  viewMode,
  setViewMode
}) {
  const { intrinsics, imageWidth, imageHeight, visibleCount, meanDistortion } = projectionData

  return (
    <aside className="controls-panel">
      <h1>Taller Camara Pinhole Calibracion</h1>
      <p className="subtitle">Implementacion Three.js: intrinsecos, extrinsecos, frustum y distorsion radial.</p>

      <div className="mode-group">
        <button
          type="button"
          className={viewMode === 'observer' ? 'mode-button active' : 'mode-button'}
          onClick={() => setViewMode('observer')}
        >
          Modo observador
        </button>
        <button
          type="button"
          className={viewMode === 'camera' ? 'mode-button active' : 'mode-button'}
          onClick={() => setViewMode('camera')}
        >
          Modo camara
        </button>
      </div>

      <section>
        <h2>Intrinsecos</h2>
        <ControlRow label="FOV (grados)" min={25} max={110} step={1} value={cameraState.fov} onChange={(value) => setCameraValue('fov', value)} />
        <ControlRow label="Aspect ratio" min={1.1} max={2.2} step={0.01} value={cameraState.aspect} onChange={(value) => setCameraValue('aspect', value)} />
        <ControlRow label="Near" min={0.1} max={20} step={0.1} value={cameraState.near} onChange={(value) => setCameraValue('near', value)} />
        <ControlRow label="Far" min={2} max={120} step={0.1} value={cameraState.far} onChange={(value) => setCameraValue('far', value)} />
      </section>

      <section>
        <h2>Extrinsecos</h2>
        <ControlRow label="Posicion X" min={-10} max={10} step={0.1} value={cameraState.x} onChange={(value) => setCameraValue('x', value)} />
        <ControlRow label="Posicion Y" min={-2} max={8} step={0.1} value={cameraState.y} onChange={(value) => setCameraValue('y', value)} />
        <ControlRow label="Posicion Z" min={1} max={16} step={0.1} value={cameraState.z} onChange={(value) => setCameraValue('z', value)} />
        <ControlRow label="Yaw" min={-180} max={180} step={1} value={cameraState.yaw} onChange={(value) => setCameraValue('yaw', value)} />
        <ControlRow label="Pitch" min={-80} max={80} step={1} value={cameraState.pitch} onChange={(value) => setCameraValue('pitch', value)} />
      </section>

      <section>
        <h2>Distorsion radial</h2>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={distortionState.enabled}
            onChange={(event) => setDistortionValue('enabled', event.target.checked)}
          />
          Activar distorsion
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={distortionState.applyTo3d}
            onChange={(event) => setDistortionValue('applyTo3d', event.target.checked)}
          />
          Aplicar al render 3D
        </label>
        <ControlRow label="k1" min={-1.2} max={1.2} step={0.01} value={distortionState.k1} onChange={(value) => setDistortionValue('k1', value)} />
        <ControlRow label="k2" min={-0.8} max={0.8} step={0.01} value={distortionState.k2} onChange={(value) => setDistortionValue('k2', value)} />
        <p className="mini-note">Tip: prueba k1=0.9 y k2=-0.35 para ver deformacion fuerte.</p>
      </section>

      <section>
        <h2>Matriz K estimada</h2>
        <pre className="matrix">
[{intrinsics.fx.toFixed(2)}   0.00  {intrinsics.cx.toFixed(2)}]
[0.00  {intrinsics.fy.toFixed(2)}  {intrinsics.cy.toFixed(2)}]
[0.00   0.00    1.00]
        </pre>
        <p className="mini-note">Imagen virtual: {imageWidth} x {imageHeight} px</p>
        <p className="mini-note">Puntos visibles: {visibleCount}/5</p>
        <p className="mini-note">Delta medio por distorsion: {meanDistortion.toFixed(2)} px</p>
      </section>
    </aside>
  )
}
