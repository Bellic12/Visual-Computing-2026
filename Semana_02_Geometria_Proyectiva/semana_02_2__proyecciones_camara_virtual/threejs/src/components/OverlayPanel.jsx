import {
  CAMERA_MODE,
  FOV_RANGE,
  ORTHO_SIZE_RANGE,
} from '../constants/cameraConfig';

const formatNumber = (value, precision = 2) =>
  typeof value === 'number' ? value.toFixed(precision) : '--';

const formatTuple = (value, precision = 2) => {
  if (!Array.isArray(value)) {
    return '--';
  }
  return `(${value.map((entry) => Number(entry).toFixed(precision)).join(', ')})`;
};

export function OverlayPanel({
  cameraMode,
  onCameraModeChange,
  fov,
  onFovChange,
  orthoSize,
  onOrthoSizeChange,
  onResetView,
  cameraTelemetry,
  projectionTelemetry,
}) {
  const perspectiveActive = cameraMode === CAMERA_MODE.PERSPECTIVE;

  return (
    <aside className="overlay-panel">
      <h1>Taller Proyecciones Camara Virtual</h1>
      <p className="panel-subtitle">
        Compara en tiempo real perspectiva vs ortografica sobre la misma escena.
      </p>

      <section className="panel-section">
        <h2>Control de camara</h2>
        <div className="toggle-group">
          <button
            type="button"
            className={perspectiveActive ? 'toggle-button active' : 'toggle-button'}
            onClick={() => onCameraModeChange(CAMERA_MODE.PERSPECTIVE)}
          >
            Perspectiva
          </button>
          <button
            type="button"
            className={!perspectiveActive ? 'toggle-button active' : 'toggle-button'}
            onClick={() => onCameraModeChange(CAMERA_MODE.ORTHOGRAPHIC)}
          >
            Ortografica
          </button>
        </div>

        <label className="slider-row" htmlFor="fov-control">
          <span>FOV (perspectiva)</span>
          <input
            id="fov-control"
            type="range"
            min={FOV_RANGE.min}
            max={FOV_RANGE.max}
            step={FOV_RANGE.step}
            value={fov}
            onChange={(event) => onFovChange(Number(event.target.value))}
          />
          <strong>{Math.round(fov)}°</strong>
        </label>

        <label className="slider-row" htmlFor="ortho-size-control">
          <span>Size (ortografica)</span>
          <input
            id="ortho-size-control"
            type="range"
            min={ORTHO_SIZE_RANGE.min}
            max={ORTHO_SIZE_RANGE.max}
            step={ORTHO_SIZE_RANGE.step}
            value={orthoSize}
            onChange={(event) => onOrthoSizeChange(Number(event.target.value))}
          />
          <strong>{orthoSize.toFixed(1)}</strong>
        </label>

        <button type="button" className="secondary-button" onClick={onResetView}>
          Reiniciar vista
        </button>
      </section>

      <section className="panel-section">
        <h2>Parametros activos</h2>
        <div className="data-grid">
          <span>Tipo</span>
          <strong>
            {perspectiveActive ? 'PerspectiveCamera' : 'OrthographicCamera'}
          </strong>

          <span>Aspect</span>
          <strong>{formatNumber(cameraTelemetry?.aspect, 3)}</strong>

          <span>Near / Far</span>
          <strong>
            {formatNumber(cameraTelemetry?.near)} / {formatNumber(cameraTelemetry?.far)}
          </strong>

          <span>FOV</span>
          <strong>{formatNumber(cameraTelemetry?.fov)}°</strong>

          <span>Left / Right</span>
          <strong>
            {formatNumber(cameraTelemetry?.left)} / {formatNumber(cameraTelemetry?.right)}
          </strong>

          <span>Top / Bottom</span>
          <strong>
            {formatNumber(cameraTelemetry?.top)} / {formatNumber(cameraTelemetry?.bottom)}
          </strong>

          <span>Posicion</span>
          <strong>{formatTuple(cameraTelemetry?.position)}</strong>

          <span>Target</span>
          <strong>{formatTuple(cameraTelemetry?.target)}</strong>
        </div>
      </section>

      <section className="panel-section">
        <h2>Transformacion 3D a 2D</h2>
        <div className="data-grid">
          <span>Punto mundo</span>
          <strong>{formatTuple(projectionTelemetry?.world)}</strong>

          <span>NDC</span>
          <strong>{formatTuple(projectionTelemetry?.ndc, 3)}</strong>

          <span>Pixel (x, y)</span>
          <strong>{formatTuple(projectionTelemetry?.screen, 1)}</strong>

          <span>Visible</span>
          <strong className={projectionTelemetry?.visible ? 'badge ok' : 'badge warn'}>
            {projectionTelemetry?.visible ? 'Si' : 'No'}
          </strong>
        </div>
        <p className="projection-note">
          Calculo realizado con <code>Vector3.project(camera)</code>.
        </p>
      </section>
    </aside>
  );
}
